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
    """Team balance calculation result"""
    team1_avg_level: float
    team2_avg_level: float
    team1_avg_stamina: float
    team2_avg_stamina: float
    team1_avg_speed: float
    team2_avg_speed: float
    level_diff: float
    stamina_diff: float
    speed_diff: float
    total_balance_score: float

class TeamCombination(NamedTuple):
    """Team combination result"""
    team1: List[Player]
    team2: List[Player]
    balance: TeamBalance

@dataclass
class TeamBalancerConfig:
    """Configuration for team balancing"""
    team_size: int = 6
    top_n_teams: int = 3
    diversity_threshold: float = 3.0
    must_be_on_different_teams: List[List[int]] = field(default_factory=lambda: [[15, 23]])
    must_be_on_same_teams: List[List[int]] = field(default_factory=list)
    stat_weights: Dict[str, float] = field(default_factory=lambda: {"level": 1.0, "stamina": 1.0, "speed": 1.0})
    
    def __post_init__(self):
        """Validate configuration"""
        if self.team_size <= 0:
            raise ValueError("Team size must be positive")
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
        if len(players) < 4:
            raise ValueError(f"Need at least 4 players to form teams, got {len(players)}")
        
        # Calculate optimal team size based on available players
        total_players = len(players)
        if total_players % 2 != 0:
            # If odd number, remove one player to make even
            total_players -= 1
        
        # Update team size to match available players
        self.config.team_size = total_players // 2
        
        logger.info(f"Adjusted team size to {self.config.team_size} for {len(players)} players")
    
    def _check_constraints(self, team1: List[Player], team2: List[Player]) -> bool:
        """Check if team combination satisfies all constraints"""
        team1_ids = {p.player_id for p in team1}
        team2_ids = {p.player_id for p in team2}
        
        # Check must-be-separate constraints
        for group in self.config.must_be_on_different_teams:
            if all(pid in team1_ids for pid in group) or all(pid in team2_ids for pid in group):
                return False
        
        # Check must-be-same constraints
        for group in self.config.must_be_on_same_teams:
            in_team1 = all(pid in team1_ids for pid in group)
            in_team2 = all(pid in team2_ids for pid in group)
            if not (in_team1 or in_team2):
                return False
        
        return True
    
    def _calculate_team_balance(self, team1: List[Player], team2: List[Player]) -> TeamBalance:
        """Calculate balance between two teams"""
        team_size = self.config.team_size
        
        # Calculate averages for team1
        team1_avg_level = sum(p.stats.level for p in team1) / team_size
        team1_avg_stamina = sum(p.stats.stamina for p in team1) / team_size
        team1_avg_speed = sum(p.stats.speed for p in team1) / team_size
        
        # Calculate averages for team2
        team2_avg_level = sum(p.stats.level for p in team2) / team_size
        team2_avg_stamina = sum(p.stats.stamina for p in team2) / team_size
        team2_avg_speed = sum(p.stats.speed for p in team2) / team_size
        
        # Calculate differences
        level_diff = abs(team1_avg_level - team2_avg_level)
        stamina_diff = abs(team1_avg_stamina - team2_avg_stamina)
        speed_diff = abs(team1_avg_speed - team2_avg_speed)
        
        # Calculate weighted total balance score
        total_balance_score = (
            level_diff * self.config.stat_weights["level"] +
            stamina_diff * self.config.stat_weights["stamina"] +
            speed_diff * self.config.stat_weights["speed"]
        )
        
        return TeamBalance(
            team1_avg_level=team1_avg_level,
            team2_avg_level=team2_avg_level,
            team1_avg_stamina=team1_avg_stamina,
            team2_avg_stamina=team2_avg_stamina,
            team1_avg_speed=team1_avg_speed,
            team2_avg_speed=team2_avg_speed,
            level_diff=level_diff,
            stamina_diff=stamina_diff,
            speed_diff=speed_diff,
            total_balance_score=total_balance_score
        )
    
    def _is_diverse_combination(self, combination: TeamCombination, 
                               existing_combinations: List[TeamCombination]) -> bool:
        """Check if combination is diverse from existing ones"""
        team1_ids = {p.player_id for p in combination.team1}
        team2_ids = {p.player_id for p in combination.team2}
        
        for existing in existing_combinations:
            existing_team1_ids = {p.player_id for p in existing.team1}
            existing_team2_ids = {p.player_id for p in existing.team2}
            
            # Check if too many players overlap
            if (len(team1_ids & existing_team1_ids) > self.config.diversity_threshold or
                len(team2_ids & existing_team2_ids) > self.config.diversity_threshold):
                return False
        
        return True
    
    def generate_balanced_teams(self, player_ids: List[int]) -> List[TeamCombination]:
        """Generate balanced teams from player IDs"""
        players = self.player_registry.get_players_by_ids(player_ids)
        self._validate_player_count(players)
        
        logger.info(f"Generating balanced teams for {len(players)} players")
        
        valid_combinations = []
        unique_combinations = set()
        
        # Generate all possible team combinations
        for team1_players in combinations(players, self.config.team_size):
            team1 = list(team1_players)
            team2 = [p for p in players if p not in team1]
            
            # Check constraints
            if not self._check_constraints(team1, team2):
                continue
            
            # Create unique key for combination
            team1_ids = tuple(sorted(p.player_id for p in team1))
            team2_ids = tuple(sorted(p.player_id for p in team2))
            combination_key = (team1_ids, team2_ids) if team1_ids < team2_ids else (team2_ids, team1_ids)
            
            if combination_key in unique_combinations:
                continue
            
            unique_combinations.add(combination_key)
            
            # Calculate balance
            balance = self._calculate_team_balance(team1, team2)
            combination = TeamCombination(team1=team1, team2=team2, balance=balance)
            valid_combinations.append(combination)
        
        logger.info(f"Found {len(valid_combinations)} valid combinations")
        
        # Apply diversity filter
        diverse_combinations = []
        for combination in valid_combinations:
            if self._is_diverse_combination(combination, diverse_combinations):
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
            team1, team2 = combination.team1, combination.team2
            
            print(f"\n**Opción {idx} - Puntuación de Balance Total: {balance.total_balance_score:.2f}**")
            print(f"**Diferencias:** Nivel: {balance.level_diff:.2f}, "
                  f"Stamina: {balance.stamina_diff:.2f}, Velocidad: {balance.speed_diff:.2f}")
            
            print(f"\n**Equipo 1 - Promedios:** Nivel: {balance.team1_avg_level:.2f}, "
                  f"Stamina: {balance.team1_avg_stamina:.2f}, Velocidad: {balance.team1_avg_speed:.2f}")
            for i, player in enumerate(team1, 1):
                positions_str = ", ".join(pos.value for pos in player.positions)
                print(f"{i}. {player.name} ({positions_str}) - "
                      f"Nivel: {player.stats.level:.1f}, "
                      f"Stamina: {player.stats.stamina:.1f}, "
                      f"Velocidad: {player.stats.speed:.1f}")

            print(f"\n**Equipo 2 - Promedios:** Nivel: {balance.team2_avg_level:.2f}, "
                  f"Stamina: {balance.team2_avg_stamina:.2f}, Velocidad: {balance.team2_avg_speed:.2f}")
            for i, player in enumerate(team2, 1):
                positions_str = ", ".join(pos.value for pos in player.positions)

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

if __name__ == "__main__":
    main()
