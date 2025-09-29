#!/usr/bin/env python3
"""
Team Balancer - Advanced football team balancing system
Provides balanced team generation based on player statistics and constraints.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import List, Dict, Set, Tuple, Optional, NamedTuple
import sys
from pathlib import Path
import json
import logging
from collections import defaultdict
import math
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Position(Enum):
    """Football positions enumeration"""
    GK = "GK"   # Goalkeeper
    DF = "DF"   # Defender
    MF = "MF"   # Midfielder
    FW = "FW"   # Forward
    LW = "LW"   # Left Winger
    RW = "RW"   # Right Winger
    CM = "CM"   # Center Midfielder
    CB = "CB"   # Center Back
    LB = "LB"   # Left Back
    RB = "RB"   # Right Back

@dataclass
class PlayerStats:
    """Player statistics with validation"""
    level: float
    stamina: float
    speed: float
    
    def __post_init__(self):
        """Validate stats are within valid range"""
        for stat_name, value in [("level", self.level), ("stamina", self.stamina), ("speed", self.speed)]:
            if not 1.0 <= value <= 5.0:
                raise ValueError(f"{stat_name} must be between 1.0 and 5.0, got {value}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {"level": self.level, "stamina": self.stamina, "speed": self.speed}

@dataclass
class Player:
    """Player model with proper ID management"""
    name: str
    positions: List[Position]
    stats: PlayerStats
    player_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate player data"""
        if not self.name.strip():
            raise ValueError("Player name cannot be empty")
        if not self.positions:
            raise ValueError("Player must have at least one position")
        if not all(isinstance(pos, Position) for pos in self.positions):
            raise ValueError("All positions must be Position enum values")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format for compatibility"""
        return {
            "Id": self.player_id,
            "Name": self.name,
            "Position": [pos.value for pos in self.positions],
            "Stats": self.stats.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> Player:
        """Create Player from dictionary"""
        return cls(
            name=data["Name"],
            positions=[Position(pos) for pos in data["Position"]],
            stats=PlayerStats(**data["Stats"]),
            player_id=data.get("Id")
        )

class TeamBalance(NamedTuple):
    """Team balance calculation result for multiple teams"""
    team_averages: List[Dict[str, float]]  # List of team averages
    balance_scores: List[float]  # Balance score for each stat
    total_balance_score: float

class TeamCombination(NamedTuple):
    """Team combination result supporting multiple teams"""
    teams: List[List[Player]]  # List of teams, each containing players
    balance: TeamBalance

@dataclass
class TeamBalancerConfig:
    """Configuration for team balancing"""
    team_size: int = 6
    num_teams: int = 2  # NEW: Number of teams to generate
    top_n_teams: int = 3
    diversity_threshold: float = 3.0
    must_be_on_different_teams: List[List[int]] = field(default_factory=lambda: [[15, 23]])
    must_be_on_same_teams: List[List[int]] = field(default_factory=list)
    must_be_on_same_teams_by_team: Dict[int, List[List[int]]] = field(default_factory=dict)
    stat_weights: Dict[str, float] = field(default_factory=lambda: {"level": 1.0, "stamina": 1.0, "speed": 1.0})
    
    def __post_init__(self):
        """Validate configuration"""
        if self.team_size <= 0:
            raise ValueError("Team size must be positive")
        if self.num_teams < 2:
            raise ValueError("Number of teams must be at least 2")
        if self.top_n_teams <= 0:
            raise ValueError("Top N teams must be positive")
        if self.diversity_threshold < 0:
            raise ValueError("Diversity threshold cannot be negative")

class PlayerRegistry:
    """Manages player IDs and provides player lookup functionality"""
    
    def __init__(self):
        self._players: Dict[int, Player] = {}
        self._next_id: int = 1
        self._name_to_id: Dict[str, int] = {}
    
    def add_player(self, player: Player) -> int:
        """Add player and assign ID if not present"""
        if player.name in self._name_to_id:
            raise ValueError(f"Player with name '{player.name}' already exists")
        
        if player.player_id is None:
            player.player_id = self._next_id
            self._next_id += 1
        elif player.player_id in self._players:
            raise ValueError(f"Player ID {player.player_id} already exists")
        
        self._players[player.player_id] = player
        self._name_to_id[player.name] = player.player_id
        return player.player_id
    
    def get_player(self, player_id: int) -> Optional[Player]:
        """Get player by ID"""
        return self._players.get(player_id)
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get player by name"""
        player_id = self._name_to_id.get(name)
        return self._players.get(player_id) if player_id else None
    
    def get_players_by_ids(self, player_ids: List[int]) -> List[Player]:
        """Get multiple players by IDs"""
        players = []
        missing_ids = []
        
        for player_id in player_ids:
            player = self._players.get(player_id)
            if player:
                players.append(player)
            else:
                missing_ids.append(player_id)
        
        if missing_ids:
            raise ValueError(f"Players with IDs {missing_ids} not found")
        
        return players
    
    def get_all_players(self) -> List[Player]:
        """Get all registered players"""
        return list(self._players.values())
    
    def remove_player(self, player_id: int) -> bool:
        """Remove player by ID"""
        if player_id not in self._players:
            return False
        
        player = self._players[player_id]
        del self._players[player_id]
        del self._name_to_id[player.name]
        return True
    
    def update_player(self, player_id: int, updated_player: Player) -> bool:
        """Update an existing player"""
        if player_id not in self._players:
            return False
        
        old_player = self._players[player_id]
        old_name = old_player.name
        new_name = updated_player.name
        
        # Remove old name mapping if name changed
        if old_name != new_name:
            if new_name in self._name_to_id and self._name_to_id[new_name] != player_id:
                raise ValueError(f"Player with name '{new_name}' already exists")
            del self._name_to_id[old_name]
            self._name_to_id[new_name] = player_id
        
        # Update the player in the registry
        updated_player.player_id = player_id  # Ensure ID is preserved
        self._players[player_id] = updated_player
        
        return True
    
    def clear(self):
        """Clear all players"""
        self._players.clear()
        self._name_to_id.clear()
        self._next_id = 1

class TeamBalancer:
    """Advanced team balancing system"""
    
    def __init__(self, config: TeamBalancerConfig, player_registry: PlayerRegistry):
        self.config = config
        self.player_registry = player_registry
        self._constraint_cache: Dict[Tuple, bool] = {}
    
    def _validate_player_count(self, players: List[Player]) -> None:
        """Validate that we have the correct number of players"""
        min_players = self.config.num_teams * 2  # Minimum 2 players per team
        if len(players) < min_players:
            raise ValueError(f"Need at least {min_players} players to form {self.config.num_teams} teams, got {len(players)}")
        
        # Calculate optimal team size based on available players and number of teams
        total_players = len(players)
        optimal_team_size = total_players // self.config.num_teams
        
        # If we have leftover players, they will be distributed or excluded
        leftover_players = total_players % self.config.num_teams
        if leftover_players > 0:
            logger.info(f"Will have {leftover_players} leftover players that will be excluded from teams")
        
        # Update team size to match available players
        self.config.team_size = optimal_team_size
        
        logger.info(f"Adjusted team size to {self.config.team_size} for {len(players)} players across {self.config.num_teams} teams")
    
    def _check_constraints(self, teams: List[List[Player]]) -> bool:
        """Check if team combination satisfies all constraints"""
        team_ids_sets = [{p.player_id for p in team} for team in teams]
        
        # Check must-be-separate constraints
        for group in self.config.must_be_on_different_teams:
            # Count how many teams contain all players from this group
            teams_with_all_players = 0
            for team_ids in team_ids_sets:
                if all(pid in team_ids for pid in group):
                    teams_with_all_players += 1
            
            # If any team contains all players from the group, constraint is violated
            if teams_with_all_players > 0:
                return False
        
        # Check must-be-same constraints
        for group in self.config.must_be_on_same_teams:
            # Check if all players in group are on the same team
            found_on_same_team = False
            for team_ids in team_ids_sets:
                if all(pid in team_ids for pid in group):
                    found_on_same_team = True
                    break
            
            if not found_on_same_team:
                return False
        
        # Check must-be-same-on-specific-team constraints (1-based team index)
        if self.config.must_be_on_same_teams_by_team:
            for team_index_1_based, groups in self.config.must_be_on_same_teams_by_team.items():
                # Validate index points to an existing team
                if not (1 <= team_index_1_based <= len(team_ids_sets)):
                    logger.warning(f"Configured team index {team_index_1_based} is out of range for current teams; failing combination.")
                    return False
                team_ids = team_ids_sets[team_index_1_based - 1]
                for group in groups:
                    if not all(pid in team_ids for pid in group):
                        return False
        
        return True
    
    def _calculate_team_balance(self, teams: List[List[Player]]) -> TeamBalance:
        """Calculate balance between multiple teams"""
        team_averages = []
        
        # Calculate averages for each team
        for team in teams:
            team_size = len(team)
            if team_size == 0:
                team_averages.append({"level": 0.0, "stamina": 0.0, "speed": 0.0})
                continue
                
            avg_level = sum(p.stats.level for p in team) / team_size
            avg_stamina = sum(p.stats.stamina for p in team) / team_size
            avg_speed = sum(p.stats.speed for p in team) / team_size
            
            team_averages.append({
                "level": avg_level,
                "stamina": avg_stamina,
                "speed": avg_speed
            })
        
        # Calculate balance scores (variance across teams for each stat)
        balance_scores = []
        stat_names = ["level", "stamina", "speed"]
        
        for stat_name in stat_names:
            stat_values = [team_avg[stat_name] for team_avg in team_averages]
            if len(stat_values) > 1:
                # Calculate variance (measure of balance)
                mean_stat = sum(stat_values) / len(stat_values)
                variance = sum((x - mean_stat) ** 2 for x in stat_values) / len(stat_values)
                balance_scores.append(math.sqrt(variance))  # Standard deviation
            else:
                balance_scores.append(0.0)
        
        # Calculate weighted total balance score (lower is better)
        total_balance_score = sum(
            score * self.config.stat_weights.get(stat_name, 1.0)
            for score, stat_name in zip(balance_scores, stat_names)
        )
        
        return TeamBalance(
            team_averages=team_averages,
            balance_scores=balance_scores,
            total_balance_score=total_balance_score
        )
    
    def _estimate_num_combinations(self, n_players, n_teams, team_size):
        """Estimate the number of ways to split n_players into n_teams of team_size each (unordered teams)"""
        from math import comb, factorial
        numerator = math.factorial(n_players)
        denominator = (math.factorial(team_size) ** n_teams) * math.factorial(n_teams)
        return numerator // denominator

    def _generate_random_team_combinations(self, players: List[Player], num_teams: int, team_size: int, n_samples: int = 10000) -> List[List[List[Player]]]:
        """Generate random team combinations (for large N)"""
        all_players = players[:]
        combinations_set = set()
        results = []
        max_attempts = n_samples * 10
        attempts = 0
        while len(results) < n_samples and attempts < max_attempts:
            attempts += 1
            random.shuffle(all_players)
            teams = [all_players[i*team_size:(i+1)*team_size] for i in range(num_teams)]
            # Ensure all teams have correct size
            if any(len(team) != team_size for team in teams):
                continue
            # Use sorted tuple of sorted player IDs for uniqueness
            key = tuple(tuple(sorted(p.player_id for p in team)) for team in teams)
            if key in combinations_set:
                continue
            combinations_set.add(key)
            results.append([team[:] for team in teams])
        return results

    def _generate_team_combinations(self, players: List[Player]) -> List[List[List[Player]]]:
        """Generate all possible team combinations, or random samples if too large"""
        num_teams = self.config.num_teams
        team_size = self.config.team_size
        total_needed = num_teams * team_size
        if len(players) > total_needed:
            players = players[:total_needed]
        elif len(players) < total_needed:
            raise ValueError(f"Not enough players: need {total_needed}, have {len(players)}")
        # Estimate number of combinations
        n_combos = self._estimate_num_combinations(len(players), num_teams, team_size)
        MAX_COMBINATIONS = 100000
        if n_combos > MAX_COMBINATIONS:
            logger.info(f"Too many combinations ({n_combos}), using random sampling.")
            return self._generate_random_team_combinations(players, num_teams, team_size, n_samples=100000)
        # Generate all ways to divide players into teams
        def distribute_players(remaining_players, teams_left, current_combination):
            if teams_left == 0:
                if len(remaining_players) == 0:
                    yield current_combination[:]
                return
            
            if teams_left == 1:
                # Last team gets all remaining players
                yield current_combination + [remaining_players[:]]
                return
            
            # Choose players for current team
            for team_players in combinations(remaining_players, team_size):
                team = list(team_players)
                new_remaining = [p for p in remaining_players if p not in team]
                yield from distribute_players(new_remaining, teams_left - 1, current_combination + [team])
        
        return list(distribute_players(players, num_teams, []))


    def _generate_constraint_aware_combinations(self, players: List[Player]) -> List[List[List[Player]]]:
        """Generate combinations that respect per-team constraints (simplified)"""
        return self._generate_team_combinations(players)
    
    def _generate_relaxed_constraint_combinations(self, players: List[Player], constraint_players: List[int]) -> List[List[List[Player]]]:
        """Generate combinations with relaxed constraints (simplified)"""
        return self._generate_team_combinations(players)
    
    def _generate_random_combinations(self, players: List[Player]) -> List[List[List[Player]]]:
        """Generate random team combinations (simplified)"""
        return self._generate_team_combinations(players)
    
    def generate_balanced_teams(self, player_ids: List[int]) -> List[TeamCombination]:
        """Generate balanced teams from player IDs"""
        players = self.player_registry.get_players_by_ids(player_ids)
        self._validate_player_count(players)
        
        logger.info(f"Generating balanced teams for {len(players)} players across {self.config.num_teams} teams")
        
        valid_combinations = []
        
        # Generate all possible team combinations
        team_combinations = self._generate_team_combinations(players)
        logger.info(f"Generated {len(team_combinations)} possible team combinations")
        
        for teams in team_combinations:
            # Check constraints
            if not self._check_constraints(teams):
                continue
            
            # Calculate balance
            balance = self._calculate_team_balance(teams)
            combination = TeamCombination(teams=teams, balance=balance)
            valid_combinations.append(combination)
        
        logger.info(f"Found {len(valid_combinations)} valid combinations")
        
        # Apply diversity filter (simplified for multiple teams)
        diverse_combinations = []
        for combination in valid_combinations:
            if len(diverse_combinations) < self.config.top_n_teams * 2:  # Keep more for diversity
                diverse_combinations.append(combination)
        
        logger.info(f"Found {len(diverse_combinations)} diverse combinations")
        
        # Sort by balance score and return top N
        diverse_combinations.sort(key=lambda x: x.balance.total_balance_score)
        return diverse_combinations[:self.config.top_n_teams]

class TeamBalancerDisplay:
    """Handles team display formatting"""
    
    @staticmethod
    def display_teams(combinations: List[TeamCombination]) -> None:
        """Display team combinations in a formatted way"""
        for idx, combination in enumerate(combinations, 1):
            balance = combination.balance
            teams = combination.teams
            
            print(f"\n**Opción {idx} - Puntuación de Balance Total: {balance.total_balance_score:.2f}**")
            
            for i, team in enumerate(teams, 1):
                print(f"\n**Equipo {i} - Promedios:**")
                for j, player in enumerate(team, 1):
                    positions_str = ", ".join(pos.value for pos in player.positions)
                    print(f"{j}. {player.name} ({positions_str}) - "
                          f"Nivel: {player.stats.level:.1f}, "
                          f"Stamina: {player.stats.stamina:.1f}, "
                          f"Velocidad: {player.stats.speed:.1f}")

def initialize_system_from_json() -> Tuple[PlayerRegistry, TeamBalancer]:
    """Initialize the system from JSON data files"""
    from config import AppConfig
    from data_manager import DataManager
    
    # Load configuration
    config = AppConfig.load()
    data_manager = DataManager(config)
    
    # Load players from JSON
    players = data_manager.load_players()
    
    if not players:
        logger.error("No players found in data/players.json")
        logger.error("Please ensure the data directory contains valid player data")
        raise FileNotFoundError("No player data found. Please run the data initialization script first.")
    
    # Create registry and add players
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Create balancer configuration
    balancer_config = TeamBalancerConfig(
        team_size=config.team_size,
        num_teams=getattr(config, 'num_teams', 2),  # Use config.num_teams with fallback
        top_n_teams=config.top_n_teams,
        diversity_threshold=config.diversity_threshold,
        must_be_on_different_teams=config.must_be_on_different_teams,
        must_be_on_same_teams=config.must_be_on_same_teams,
        stat_weights=config.stat_weights
    )
    
    # Create balancer
    balancer = TeamBalancer(balancer_config, registry)
    
    logger.info(f"Initialized system with {len(players)} players from JSON data")
    return registry, balancer

def main():
    """Main function using JSON data"""
    try:
        # Initialize system from JSON
        registry, balancer = initialize_system_from_json()
        
        # Today's players (using player IDs from JSON data)
        # You can modify these IDs based on your current players
        players_today_ids = [11, 23, 20, 29, 37, 14, 33, 8, 18, 36, 38, 1]
        
        # Validate that all players exist
        try:
            balancer.player_registry.get_players_by_ids(players_today_ids)
        except ValueError as e:
            logger.error(f"Invalid player IDs: {e}")
            logger.info("Available player IDs:")
            for player in registry.get_all_players():
                logger.info(f"  ID {player.player_id}: {player.name}")
            sys.exit(1)
        
        # Generate teams
        combinations = balancer.generate_balanced_teams(players_today_ids)
        
        # Display results
        TeamBalancerDisplay.display_teams(combinations)
        
    except FileNotFoundError as e:
        logger.error(f"Data file error: {e}")
        logger.info("To fix this, run: python initialize_data.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

