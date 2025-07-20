#!/usr/bin/env python3

import unittest
import sys
import os

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from team_balancer import (
    generate_balanced_teams, 
    display_teams, 
    filter_and_validate_positions,
    POSITIONS_ALLOWED,
    TEAM_SIZE
)

class TestTeamBalancer(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_players = [
            {"Id": 1, "Name": "Player1", "Position": ["DF"], "Stats": {"level": 3.0, "stamina": 3.2, "speed": 2.8}},
            {"Id": 2, "Name": "Player2", "Position": ["FW"], "Stats": {"level": 4.0, "stamina": 3.5, "speed": 4.1}},
            {"Id": 3, "Name": "Player3", "Position": ["MF"], "Stats": {"level": 3.5, "stamina": 4.2, "speed": 3.1}},
            {"Id": 4, "Name": "Player4", "Position": ["GK"], "Stats": {"level": 2.5, "stamina": 2.8, "speed": 2.5}},
            {"Id": 5, "Name": "Player5", "Position": ["DF"], "Stats": {"level": 3.8, "stamina": 3.8, "speed": 3.0}},
            {"Id": 6, "Name": "Player6", "Position": ["FW"], "Stats": {"level": 4.2, "stamina": 3.7, "speed": 4.3}},
            {"Id": 7, "Name": "Player7", "Position": ["MF"], "Stats": {"level": 3.2, "stamina": 3.0, "speed": 3.2}},
            {"Id": 8, "Name": "Player8", "Position": ["GK"], "Stats": {"level": 3.7, "stamina": 3.4, "speed": 2.9}},
            {"Id": 9, "Name": "Player9", "Position": ["DF"], "Stats": {"level": 2.8, "stamina": 2.5, "speed": 2.7}},
            {"Id": 10, "Name": "Player10", "Position": ["FW"], "Stats": {"level": 3.9, "stamina": 3.6, "speed": 3.8}},
            {"Id": 11, "Name": "Player11", "Position": ["MF"], "Stats": {"level": 4.1, "stamina": 4.3, "speed": 3.4}},
            {"Id": 12, "Name": "Player12", "Position": ["GK"], "Stats": {"level": 3.3, "stamina": 3.1, "speed": 2.6}},
        ]
        
        # Players with multiple positions
        self.multi_position_players = [
            {"Id": 1, "Name": "Player1", "Position": ["DF", "MF"], "Stats": {"level": 3.0, "stamina": 3.2, "speed": 2.8}},
            {"Id": 2, "Name": "Player2", "Position": ["FW", "MF"], "Stats": {"level": 4.0, "stamina": 3.5, "speed": 4.1}},
            {"Id": 3, "Name": "Player3", "Position": ["MF", "DF"], "Stats": {"level": 3.5, "stamina": 4.2, "speed": 3.1}},
            {"Id": 4, "Name": "Player4", "Position": ["GK"], "Stats": {"level": 2.5, "stamina": 2.8, "speed": 2.5}},
            {"Id": 5, "Name": "Player5", "Position": ["DF", "GK"], "Stats": {"level": 3.8, "stamina": 3.8, "speed": 3.0}},
            {"Id": 6, "Name": "Player6", "Position": ["FW"], "Stats": {"level": 4.2, "stamina": 3.7, "speed": 4.3}},
            {"Id": 7, "Name": "Player7", "Position": ["MF", "FW"], "Stats": {"level": 3.2, "stamina": 3.0, "speed": 3.2}},
            {"Id": 8, "Name": "Player8", "Position": ["GK", "DF"], "Stats": {"level": 3.7, "stamina": 3.4, "speed": 2.9}},
            {"Id": 9, "Name": "Player9", "Position": ["DF"], "Stats": {"level": 2.8, "stamina": 2.5, "speed": 2.7}},
            {"Id": 10, "Name": "Player10", "Position": ["FW", "MF"], "Stats": {"level": 3.9, "stamina": 3.6, "speed": 3.8}},
            {"Id": 11, "Name": "Player11", "Position": ["MF"], "Stats": {"level": 4.1, "stamina": 4.3, "speed": 3.4}},
            {"Id": 12, "Name": "Player12", "Position": ["GK", "MF"], "Stats": {"level": 3.3, "stamina": 3.1, "speed": 2.6}},
        ]

    def test_filter_and_validate_positions(self):
        """Test position filtering and validation"""
        # Test valid positions
        player = {"Id": 1, "Name": "Test", "Position": ["DF", "MF"], "Stats": {"level": 3.0, "stamina": 3.2, "speed": 2.8}}
        result = filter_and_validate_positions(player, POSITIONS_ALLOWED)
        self.assertEqual(result["Position"], ["DF", "MF"])
        
        # Test invalid position (should raise SystemExit)
        player_invalid = {"Id": 1, "Name": "Test", "Position": ["DF", "INVALID"], "Stats": {"level": 3.0, "stamina": 3.2, "speed": 2.8}}
        with self.assertRaises(SystemExit):
            filter_and_validate_positions(player_invalid, POSITIONS_ALLOWED)

    def test_generate_balanced_teams_basic(self):
        """Test basic team generation without constraints"""
        result = generate_balanced_teams(self.test_players, team_size=6, must_be_separate=[], must_be_same=[], top_n=3)
        
        # Should return list of tuples
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Each result should be a tuple with 9 elements
        for team_combo in result:
            self.assertEqual(len(team_combo), 9)
            team1, team2, team1_avg, team2_avg, total_score, team1_stamina, team2_stamina, team1_speed, team2_speed = team_combo
            
            # Teams should have correct size
            self.assertEqual(len(team1), 6)
            self.assertEqual(len(team2), 6)
            
            # All players should be unique
            team1_ids = {p["Id"] for p in team1}
            team2_ids = {p["Id"] for p in team2}
            self.assertEqual(len(team1_ids), 6)
            self.assertEqual(len(team2_ids), 6)
            self.assertEqual(len(team1_ids & team2_ids), 0)  # No overlap
            
            # Average levels should be calculated correctly
            expected_team1_avg = sum(p["Stats"]["level"] for p in team1) / 6
            expected_team2_avg = sum(p["Stats"]["level"] for p in team2) / 6
            self.assertAlmostEqual(team1_avg, expected_team1_avg, places=2)
            self.assertAlmostEqual(team2_avg, expected_team2_avg, places=2)
            
            # Total balance score should be calculated correctly (sum of all stat differences)
            expected_level_diff = abs(team1_avg - team2_avg)
            expected_stamina_diff = abs(team1_stamina - team2_stamina)
            expected_speed_diff = abs(team1_speed - team2_speed)
            expected_total_score = expected_level_diff + expected_stamina_diff + expected_speed_diff
            self.assertAlmostEqual(total_score, expected_total_score, places=2)

    def test_generate_balanced_teams_with_constraints(self):
        """Test team generation with must-be-separate constraints"""
        # Players 1 and 2 must be on different teams
        result = generate_balanced_teams(
            self.test_players, 
            team_size=6, 
            must_be_separate=[[1, 2]], 
            must_be_same=[], 
            top_n=3
        )
        
        self.assertGreater(len(result), 0)
        
        # Check that players 1 and 2 are never on the same team
        for team_combo in result:
            team1, team2, _, _, _, _, _, _, _ = team_combo
            team1_ids = {p["Id"] for p in team1}
            team2_ids = {p["Id"] for p in team2}
            
            # Player 1 and 2 should not be in the same team
            self.assertFalse(1 in team1_ids and 2 in team1_ids)
            self.assertFalse(1 in team2_ids and 2 in team2_ids)

    def test_generate_balanced_teams_with_same_team_constraints(self):
        """Test team generation with must-be-same constraints"""
        # Players 1 and 2 must be on the same team
        result = generate_balanced_teams(
            self.test_players, 
            team_size=6, 
            must_be_separate=[], 
            must_be_same=[[1, 2]], 
            top_n=3
        )
        
        self.assertGreater(len(result), 0)
        
        # Check that players 1 and 2 are always on the same team
        for team_combo in result:
            team1, team2, _, _, _, _, _, _, _ = team_combo
            team1_ids = {p["Id"] for p in team1}
            team2_ids = {p["Id"] for p in team2}
            
            # Player 1 and 2 should be in the same team
            both_in_team1 = 1 in team1_ids and 2 in team1_ids
            both_in_team2 = 1 in team2_ids and 2 in team2_ids
            self.assertTrue(both_in_team1 or both_in_team2)

    def test_multi_position_players(self):
        """Test that players with multiple positions work correctly"""
        result = generate_balanced_teams(
            self.multi_position_players, 
            team_size=6, 
            must_be_separate=[], 
            must_be_same=[], 
            top_n=3
        )
        
        self.assertGreater(len(result), 0)
        
        # Verify all players have valid positions
        for team_combo in result:
            team1, team2, _, _, _, _, _, _, _ = team_combo
            all_players = team1 + team2
            
            for player in all_players:
                for position in player["Position"]:
                    self.assertIn(position, POSITIONS_ALLOWED)

    def test_team_balance_optimization(self):
        """Test that teams are sorted by balance (lowest rating difference first)"""
        result = generate_balanced_teams(
            self.test_players, 
            team_size=6, 
            must_be_separate=[], 
            must_be_same=[], 
            top_n=5
        )
        
        if len(result) > 1:
            # Check that results are sorted by total balance score (ascending)
            for i in range(len(result) - 1):
                self.assertLessEqual(result[i][4], result[i + 1][4])  # total_score should be <= next total_score

    def test_diversity_filter(self):
        """Test that diversity filter works correctly"""
        result = generate_balanced_teams(
            self.test_players, 
            team_size=6, 
            must_be_separate=[], 
            must_be_same=[], 
            top_n=3,
            diversity_threshold=3  # Teams should share at most 3 players
        )
        
        if len(result) > 1:
            # Check diversity between consecutive results
            for i in range(len(result) - 1):
                team1_a, team2_a, _, _, _, _, _, _, _ = result[i]
                team1_b, team2_b, _, _, _, _, _, _, _ = result[i + 1]
                
                team1_a_ids = {p["Id"] for p in team1_a}
                team1_b_ids = {p["Id"] for p in team1_b}
                team2_a_ids = {p["Id"] for p in team2_a}
                team2_b_ids = {p["Id"] for p in team2_b}
                
                # Teams should not share more than 3 players
                self.assertLessEqual(len(team1_a_ids & team1_b_ids), 3)
                self.assertLessEqual(len(team2_a_ids & team2_b_ids), 3)

    def test_edge_cases(self):
        """Test edge cases"""
        # Test with minimum valid team size
        result = generate_balanced_teams(
            self.test_players[:4], 
            team_size=2, 
            must_be_separate=[], 
            must_be_same=[], 
            top_n=1
        )
        
        if result:
            team1, team2, _, _, _, _, _, _, _ = result[0]
            self.assertEqual(len(team1), 2)
            self.assertEqual(len(team2), 2)

    def test_stats_structure(self):
        """Test that all players have the correct Stats structure"""
        for player in self.test_players:
            # Check that Stats field exists
            self.assertIn("Stats", player)
            
            # Check that Stats has all required fields
            stats = player["Stats"]
            self.assertIn("level", stats)
            self.assertIn("stamina", stats)
            self.assertIn("speed", stats)
            
            # Check that level is a number
            self.assertIsInstance(stats["level"], (int, float))
            
            # Check that stamina and speed are numbers (defaulting to 0)
            self.assertIsInstance(stats["stamina"], (int, float))
            self.assertIsInstance(stats["speed"], (int, float))

    def test_level_calculation(self):
        """Test that level is used correctly for team balance calculations"""
        # Create players with very different levels to make balance obvious
        unbalanced_players = [
            {"Id": 1, "Name": "High1", "Position": ["FW"], "Stats": {"level": 5.0, "stamina": 4.8, "speed": 4.5}},
            {"Id": 2, "Name": "High2", "Position": ["FW"], "Stats": {"level": 5.0, "stamina": 4.7, "speed": 4.6}},
            {"Id": 3, "Name": "High3", "Position": ["FW"], "Stats": {"level": 5.0, "stamina": 4.9, "speed": 4.4}},
            {"Id": 4, "Name": "Low1", "Position": ["DF"], "Stats": {"level": 1.0, "stamina": 1.5, "speed": 1.8}},
            {"Id": 5, "Name": "Low2", "Position": ["DF"], "Stats": {"level": 1.0, "stamina": 1.2, "speed": 1.5}},
            {"Id": 6, "Name": "Low3", "Position": ["DF"], "Stats": {"level": 1.0, "stamina": 1.8, "speed": 1.3}},
        ]
        
        result = generate_balanced_teams(
            unbalanced_players, 
            team_size=3, 
            must_be_separate=[], 
            must_be_same=[], 
            top_n=1
        )
        
        if result:
            team1, team2, team1_avg, team2_avg, total_score, team1_stamina, team2_stamina, team1_speed, team2_speed = result[0]
            
            # The best balance should have 2 high-level and 1 low-level player in each team
            # This would give average levels of (5+5+1)/3 = 3.67 and (5+1+1)/3 = 2.33
            # Or similar balanced combinations
            
            # Check that the total balance score is reasonable (not too high)
            self.assertLess(total_score, 6.0)  # Should be well balanced across all stats

if __name__ == '__main__':
    unittest.main() 