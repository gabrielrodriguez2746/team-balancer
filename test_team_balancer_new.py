#!/usr/bin/env python3
"""
Comprehensive test suite for the new Team Balancer architecture
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team_balancer import (
    Player, PlayerStats, Position, PlayerRegistry, TeamBalancer, 
    TeamBalancerConfig, TeamCombination, TeamBalance
)
from config import AppConfig
from data_manager import DataManager

class TestPlayerModel(unittest.TestCase):
    """Test Player and PlayerStats models"""
    
    def test_player_stats_validation(self):
        """Test PlayerStats validation"""
        # Valid stats
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        self.assertEqual(stats.level, 3.0)
        self.assertEqual(stats.stamina, 4.0)
        self.assertEqual(stats.speed, 2.5)
        
        # Invalid stats should raise ValueError
        with self.assertRaises(ValueError):
            PlayerStats(level=6.0, stamina=4.0, speed=2.5)  # level > 5.0
        
        with self.assertRaises(ValueError):
            PlayerStats(level=3.0, stamina=0.5, speed=2.5)  # stamina < 1.0
    
    def test_player_creation(self):
        """Test Player creation and validation"""
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        player = Player(
            name="Test Player",
            positions=[Position.DF, Position.MF],
            stats=stats,
            player_id=1
        )
        
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.positions, [Position.DF, Position.MF])
        self.assertEqual(player.stats, stats)
        self.assertEqual(player.player_id, 1)
        
        # Test validation
        with self.assertRaises(ValueError):
            Player(name="", positions=[Position.DF], stats=stats)  # Empty name
        
        with self.assertRaises(ValueError):
            Player(name="Test", positions=[], stats=stats)  # No positions
    
    def test_player_serialization(self):
        """Test Player serialization to/from dict"""
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        player = Player(
            name="Test Player",
            positions=[Position.DF, Position.MF],
            stats=stats,
            player_id=1
        )
        
        # Test to_dict
        player_dict = player.to_dict()
        expected = {
            "Id": 1,
            "Name": "Test Player",
            "Position": ["DF", "MF"],
            "Stats": {"level": 3.0, "stamina": 4.0, "speed": 2.5}
        }
        self.assertEqual(player_dict, expected)
        
        # Test from_dict
        new_player = Player.from_dict(player_dict)
        self.assertEqual(new_player.name, player.name)
        self.assertEqual(new_player.positions, player.positions)
        self.assertEqual(new_player.stats.level, player.stats.level)
        self.assertEqual(new_player.player_id, player.player_id)

class TestPlayerRegistry(unittest.TestCase):
    """Test PlayerRegistry functionality"""
    
    def setUp(self):
        self.registry = PlayerRegistry()
    
    def test_add_player(self):
        """Test adding players to registry"""
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        player = Player(
            name="Test Player",
            positions=[Position.DF],
            stats=stats
        )
        
        player_id = self.registry.add_player(player)
        self.assertEqual(player_id, 1)
        self.assertEqual(player.player_id, 1)
        
        # Test duplicate name
        player2 = Player(
            name="Test Player",  # Same name
            positions=[Position.MF],
            stats=stats
        )
        with self.assertRaises(ValueError):
            self.registry.add_player(player2)
    
    def test_get_player(self):
        """Test retrieving players from registry"""
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        player = Player(
            name="Test Player",
            positions=[Position.DF],
            stats=stats
        )
        
        self.registry.add_player(player)
        
        # Test get by ID
        retrieved = self.registry.get_player(1)
        self.assertEqual(retrieved, player)
        
        # Test get by name
        retrieved = self.registry.get_player_by_name("Test Player")
        self.assertEqual(retrieved, player)
        
        # Test non-existent player
        self.assertIsNone(self.registry.get_player(999))
        self.assertIsNone(self.registry.get_player_by_name("Non-existent"))
    
    def test_get_players_by_ids(self):
        """Test retrieving multiple players by IDs"""
        # Add multiple players
        players = []
        for i in range(3):
            stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
            player = Player(
                name=f"Player {i}",
                positions=[Position.DF],
                stats=stats
            )
            self.registry.add_player(player)
            players.append(player)
        
        # Test successful retrieval
        retrieved = self.registry.get_players_by_ids([1, 2, 3])
        self.assertEqual(len(retrieved), 3)
        
        # Test with missing ID
        with self.assertRaises(ValueError):
            self.registry.get_players_by_ids([1, 999, 3])

class TestTeamBalancer(unittest.TestCase):
    """Test TeamBalancer functionality"""
    
    def setUp(self):
        self.registry = PlayerRegistry()
        self.config = TeamBalancerConfig(
            team_size=3,
            top_n_teams=2,
            diversity_threshold=1.0
        )
        self.balancer = TeamBalancer(self.config, self.registry)
        
        # Add test players
        self.test_players = []
        for i in range(6):
            stats = PlayerStats(
                level=3.0 + (i * 0.3),  # Max: 4.5
                stamina=3.0 + (i * 0.2),  # Max: 4.2
                speed=3.0 + (i * 0.2)   # Max: 4.2
            )
            player = Player(
                name=f"Player {i}",
                positions=[Position.DF],
                stats=stats
            )
            self.registry.add_player(player)
            self.test_players.append(player)
    
    def test_validate_player_count(self):
        """Test player count validation"""
        # Valid count
        players = self.registry.get_players_by_ids([1, 2, 3, 4, 5, 6])
        self.balancer._validate_player_count(players)  # Should not raise
        
        # Invalid count
        players = self.registry.get_players_by_ids([1, 2, 3])
        with self.assertRaises(ValueError):
            self.balancer._validate_player_count(players)
    
    def test_check_constraints(self):
        """Test constraint checking"""
        team1 = self.registry.get_players_by_ids([1, 2, 3])
        team2 = self.registry.get_players_by_ids([4, 5, 6])
        
        # Test without constraints
        self.assertTrue(self.balancer._check_constraints(team1, team2))
        
        # Test with must-be-separate constraint
        self.config.must_be_on_different_teams = [[1, 2]]
        self.assertFalse(self.balancer._check_constraints(team1, team2))
        
        # Test with must-be-same constraint
        self.config.must_be_on_different_teams = []
        self.config.must_be_on_same_teams = [[1, 4]]
        self.assertFalse(self.balancer._check_constraints(team1, team2))
    
    def test_calculate_team_balance(self):
        """Test team balance calculation"""
        team1 = self.registry.get_players_by_ids([1, 2, 3])
        team2 = self.registry.get_players_by_ids([4, 5, 6])
        
        balance = self.balancer._calculate_team_balance(team1, team2)
        
        self.assertIsInstance(balance, TeamBalance)
        self.assertGreater(balance.total_balance_score, 0)
        
        # Test stat weights
        self.config.stat_weights = {"level": 2.0, "stamina": 1.0, "speed": 1.0}
        balance_weighted = self.balancer._calculate_team_balance(team1, team2)
        self.assertNotEqual(balance.total_balance_score, balance_weighted.total_balance_score)
    
    def test_generate_balanced_teams(self):
        """Test team generation"""
        player_ids = [1, 2, 3, 4, 5, 6]
        combinations = self.balancer.generate_balanced_teams(player_ids)
        
        self.assertIsInstance(combinations, list)
        self.assertLessEqual(len(combinations), self.config.top_n_teams)
        
        for combination in combinations:
            self.assertIsInstance(combination, TeamCombination)
            self.assertEqual(len(combination.team1), self.config.team_size)
            self.assertEqual(len(combination.team2), self.config.team_size)
            
            # Check no overlap between teams
            team1_ids = {p.player_id for p in combination.team1}
            team2_ids = {p.player_id for p in combination.team2}
            self.assertEqual(len(team1_ids & team2_ids), 0)

class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_app_config_creation(self):
        """Test AppConfig creation and validation"""
        config = AppConfig()
        
        self.assertEqual(config.team_size, 6)
        self.assertEqual(config.top_n_teams, 3)
        self.assertEqual(config.diversity_threshold, 3.0)
        
        # Test validation - these should not raise errors as validation is in TeamBalancerConfig
        # AppConfig itself doesn't validate these values
        config_invalid = AppConfig(team_size=0)
        self.assertEqual(config_invalid.team_size, 0)
    
    def test_config_serialization(self):
        """Test configuration serialization"""
        config = AppConfig(
            team_size=4,
            top_n_teams=2,
            stat_weights={"level": 2.0, "stamina": 1.0, "speed": 1.0}
        )
        
        config_dict = config.to_dict()
        new_config = AppConfig.from_dict(config_dict)
        
        self.assertEqual(new_config.team_size, config.team_size)
        self.assertEqual(new_config.top_n_teams, config.top_n_teams)
        self.assertEqual(new_config.stat_weights, config.stat_weights)
    
    def test_config_file_operations(self):
        """Test configuration file save/load"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AppConfig()
            config.config_file = Path(temp_dir) / "test_config.json"
            
            # Test save
            config.save()
            self.assertTrue(config.config_file.exists())
            
            # Test load
            loaded_config = AppConfig.load()
            self.assertEqual(loaded_config.team_size, config.team_size)

class TestDataManager(unittest.TestCase):
    """Test DataManager functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = AppConfig()
        self.config.data_dir = Path(self.temp_dir)
        self.config.players_file = Path(self.temp_dir) / "players.json"
        self.data_manager = DataManager(self.config)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_players(self):
        """Test player data persistence"""
        # Create test players
        players = []
        for i in range(3):
            stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
            player = Player(
                name=f"Player {i}",
                positions=[Position.DF],
                stats=stats,
                player_id=i + 1
            )
            players.append(player)
        
        # Test save
        self.data_manager.save_players(players)
        self.assertTrue(self.config.players_file.exists())
        
        # Test load
        loaded_players = self.data_manager.load_players()
        self.assertEqual(len(loaded_players), 3)
        
        for original, loaded in zip(players, loaded_players):
            self.assertEqual(original.name, loaded.name)
            self.assertEqual(original.positions, loaded.positions)
            self.assertEqual(original.stats.level, loaded.stats.level)
    
    def test_player_validation(self):
        """Test player data validation"""
        # Valid players
        stats = PlayerStats(level=3.0, stamina=4.0, speed=2.5)
        valid_players = [
            Player(name="Player 1", positions=[Position.DF], stats=stats),
            Player(name="Player 2", positions=[Position.MF], stats=stats)
        ]
        
        errors = self.data_manager.validate_player_data(valid_players)
        self.assertEqual(len(errors), 0)
        
        # Invalid players - duplicate names
        invalid_players = [
            Player(name="Player 1", positions=[Position.DF], stats=stats),
            Player(name="Player 1", positions=[Position.MF], stats=stats)  # Duplicate name
        ]
        
        errors = self.data_manager.validate_player_data(invalid_players)
        self.assertGreater(len(errors), 0)
        self.assertIn("Duplicate player names", errors[0])
    
    def test_player_statistics(self):
        """Test player statistics generation"""
        # Add players to registry
        for i in range(3):
            stats = PlayerStats(
                level=3.0 + (i * 0.5),  # Max: 4.0
                stamina=4.0 + (i * 0.3),  # Max: 4.6
                speed=2.5 + (i * 0.4)   # Max: 3.3
            )
            player = Player(
                name=f"Player {i}",
                positions=[Position.DF],
                stats=stats
            )
            self.data_manager.registry.add_player(player)
        
        stats = self.data_manager.get_player_statistics()
        
        self.assertEqual(stats['total_players'], 3)
        self.assertIn('level_stats', stats)
        self.assertIn('stamina_stats', stats)
        self.assertIn('speed_stats', stats)
        self.assertEqual(stats['level_stats']['min'], 3.0)
        self.assertEqual(stats['level_stats']['max'], 4.0)  # 3.0 + (2 * 0.5) = 4.0

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow from player creation to team generation"""
        # Setup
        registry = PlayerRegistry()
        config = TeamBalancerConfig(team_size=3, top_n_teams=2)
        balancer = TeamBalancer(config, registry)
        
        # Create players
        players = []
        for i in range(6):
            stats = PlayerStats(
                level=3.0 + (i * 0.3),  # Max: 4.5
                stamina=3.0 + (i * 0.2),  # Max: 4.2
                speed=3.0 + (i * 0.2)   # Max: 4.2
            )
            player = Player(
                name=f"Player {i}",
                positions=[Position.DF],
                stats=stats
            )
            registry.add_player(player)
            players.append(player)
        
        # Generate teams
        player_ids = [p.player_id for p in players]
        combinations = balancer.generate_balanced_teams(player_ids)
        
        # Verify results
        self.assertIsInstance(combinations, list)
        self.assertGreater(len(combinations), 0)
        
        for combination in combinations:
            self.assertIsInstance(combination, TeamCombination)
            self.assertEqual(len(combination.team1), 3)
            self.assertEqual(len(combination.team2), 3)
            
            # Verify no player overlap
            team1_ids = {p.player_id for p in combination.team1}
            team2_ids = {p.player_id for p in combination.team2}
            self.assertEqual(len(team1_ids & team2_ids), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2) 