#!/usr/bin/env python3
"""
Team Balancer - Advanced football team balancing system
Provides balanced team generation based on player statistics and constraints.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import List, Dict, Set, Tuple, Optional, NamedTuple, Any
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
    """
    Configuration for team balancing.

    must_be_on_same_teams_by_team:
        Dict[int, List[List[int]]] mapping 1-based team index to list of groups of player IDs.
        Each group must be assigned together on the specified team.
        Example: {1: [[1,10,15,12]], 2: [[3,2]]}
    """
    team_size: int = 6
    num_teams: int = 2  # Number of teams to generate
    top_n_teams: int = 5  # Increased to show more options
    diversity_threshold: float = 1.5  # Lowered to allow more diverse combinations
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
        
        # Check must-be-same constraints
        for group in self.config.must_be_on_same_teams:
            # All players in group must be on the same team
            if not any(all(pid in team_ids for pid in group) for team_ids in team_ids_sets):
                return False

        # Check must-be-same-on-specific-team constraints (1-based team index)
        for team_index_1_based, groups in self.config.must_be_on_same_teams_by_team.items():
            # Validate index points to an existing team
            if not (1 <= team_index_1_based <= len(team_ids_sets)):
                logger.warning(f"Configured team index {team_index_1_based} is out of range for current teams; failing combination.")
                return False
            team_ids = team_ids_sets[team_index_1_based - 1]
            # All groups must have all players on the specified team
            if not all(all(pid in team_ids for pid in group) for group in groups):
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
    
    def _estimate_num_combinations(self, n_players: int, n_teams: int, team_size: int) -> int:
        """Estimate the number of ways to split n_players into n_teams of team_size each (unordered teams)"""
        numerator = math.factorial(n_players)
        denominator = (math.factorial(team_size) ** n_teams) * math.factorial(n_teams)
        return numerator // denominator

    def _generate_random_team_combinations(self, players: List[Player], num_teams: int, team_size: int, n_samples: int = 50000) -> List[List[List[Player]]]:
        """Generate random team combinations (for large N) - increased samples for better diversity"""
        seen_combinations = set()
        results = []
        max_attempts = n_samples * 20  # Increased attempts to find unique combinations
        
        for attempt in range(max_attempts):
            if len(results) >= n_samples:
                break
                
            shuffled = players.copy()
            random.shuffle(shuffled)
            teams = [shuffled[i*team_size:(i+1)*team_size] for i in range(num_teams)]
            
            # Ensure all teams have correct size
            if any(len(team) != team_size for team in teams):
                continue
            
            # Use sorted tuple of sorted player IDs for uniqueness
            combination_key = tuple(tuple(sorted(p.player_id for p in team)) for team in teams)
            if combination_key in seen_combinations:
                continue
                
            seen_combinations.add(combination_key)
            results.append([team.copy() for team in teams])
        
        logger.info(f"Generated {len(results)} unique random combinations")
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
        MAX_COMBINATIONS = 50000  # Lower threshold to use random sampling more often for better diversity
        if n_combos > MAX_COMBINATIONS:
            # Use more samples to increase probability of finding diverse combinations
            sample_size = min(50000, n_combos // 10)  # Sample 10% or up to 50k
            logger.info(f"Too many combinations ({n_combos}), using random sampling with {sample_size} samples.")
            return self._generate_random_team_combinations(players, num_teams, team_size, n_samples=sample_size)
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

    def _calculate_team_diversity(self, combination: TeamCombination, existing_combinations: List[TeamCombination], enforce_3_player_limit: bool = True) -> float:
        """Calculate how different this combination is from existing ones (1.0 = completely different, 0.0 = identical)
        
        Logic: A combination is valid if no team in it shares more than 3 players with any team 
        from any existing combination.
        
        Args:
            combination: The combination to evaluate
            existing_combinations: List of already selected combinations
            enforce_3_player_limit: If True, returns -1.0 if any team shares >3 players with any existing team (reject). If False, calculates score anyway.
        """
        if not existing_combinations:
            return 1.0
        
        current_team_sets = [set(p.player_id for p in team) for team in combination.teams]
        max_overlap = 0.0
        max_team_overlap = 0  # Track maximum overlap between any two specific teams
        
        for existing in existing_combinations:
            existing_team_sets = [set(p.player_id for p in team) for team in existing.teams]
            
            # Check each team in new combination against each team in existing combination
            for current_team in current_team_sets:
                for existing_team in existing_team_sets:
                    if current_team and existing_team:
                        # Count overlapping players between these two specific teams
                        overlap_count = len(current_team & existing_team)
                        max_team_overlap = max(max_team_overlap, overlap_count)
                        
                        # Calculate overlap percentage for diversity score
                        overlap_ratio = overlap_count / len(current_team | existing_team)
                        max_overlap = max(max_overlap, overlap_ratio)
            
            # If enforcing 3-player limit and any team pair has more than 3 overlapping players, reject
            if enforce_3_player_limit and max_team_overlap > 3:
                return -1.0
        
        diversity = 1.0 - max_overlap
        
        # If not enforcing limit but max team overlap > 3, penalize the score
        if not enforce_3_player_limit and max_team_overlap > 3:
            # Heavily penalize but don't completely reject
            penalty = (max_team_overlap - 3) * 0.2
            diversity = max(0.0, diversity - penalty)
        
        return diversity

    def _combinations_equal(self, combo1: TeamCombination, combo2: TeamCombination) -> bool:
        """Check if two combinations are identical (same teams)"""
        if len(combo1.teams) != len(combo2.teams):
            return False
        
        # Compare team sets (order-independent)
        combo1_teams = [tuple(sorted(p.player_id for p in team)) for team in combo1.teams]
        combo2_teams = [tuple(sorted(p.player_id for p in team)) for team in combo2.teams]
        
        # Sort team sets for comparison
        combo1_teams.sort()
        combo2_teams.sort()
        
        return combo1_teams == combo2_teams

    def _analyze_player_pool(self, players: List[Player]) -> Dict[str, Any]:
        """Analyze player pool to determine optimal combination generation strategy
        
        Returns a dictionary with:
        - total_players: Number of players
        - num_teams: Number of teams to form
        - team_size: Size of each team
        - theoretical_max_combinations: Estimated maximum possible combinations
        - difficulty_score: Score indicating how difficult it will be to find diverse combinations (0-1)
        - recommended_pool_size: Recommended number of combinations to generate
        - recommended_sample_size: Recommended sample size for random generation
        """
        num_teams = self.config.num_teams
        team_size = self.config.team_size
        total_players = len(players)
        total_players_needed = num_teams * team_size
        
        # Calculate theoretical maximum combinations
        theoretical_max = self._estimate_num_combinations(total_players, num_teams, team_size)
        
        # Analyze diversity difficulty
        # Factors:
        # 1. Player pool size relative to needed (larger pool = easier diversity)
        # 2. Number of players that can be different between combinations
        # 3. Constraint density (more constraints = harder to find diverse combinations)
        
        # Calculate how many players can vary between combinations
        players_per_combination = num_teams * team_size
        players_that_can_differ = total_players - players_per_combination
        
        # Difficulty score: 0 = easy (many diverse options), 1 = hard (few diverse options)
        # If players_that_can_differ is negative or very small, it's very hard
        if players_that_can_differ <= 0:
            difficulty_score = 1.0
        else:
            # Difficulty increases as the ratio of fixed players increases
            # If we need all players, difficulty is 1.0
            # If we can choose from many extras, difficulty decreases
            fixed_ratio = players_per_combination / total_players
            # Also consider that with only 3 allowed repeats, we need significant variation
            # A combination uses 'players_per_combination' players
            # For 3 diverse combinations with max 3 repeats, we need at least:
            # players_per_combination * 3 - (3 * 2) = players_per_combination * 3 - 6 unique player assignments
            min_unique_assignments = (players_per_combination * 3) - 6
            if total_players < min_unique_assignments:
                difficulty_score = min(1.0, 1.0 - (total_players / min_unique_assignments))
            else:
                # Difficulty based on fixed ratio and available variation
                difficulty_score = max(0.0, min(1.0, fixed_ratio * 1.5 - 0.3))
        
        # Calculate recommended pool size based on difficulty and theoretical max
        # For easy cases: smaller pool is fine
        # For hard cases: need much larger pool to find 3 diverse combinations
        base_pool_multiplier = 50  # Base multiplier for finding diverse combinations
        difficulty_multiplier = 1 + (difficulty_score * 9)  # 1x to 10x based on difficulty
        recommended_pool_size = int(base_pool_multiplier * difficulty_multiplier * 3)  # At least 3 combinations needed
        
        # Cap at reasonable maximum
        max_reasonable_pool = min(theoretical_max, 50000)
        recommended_pool_size = min(recommended_pool_size, max_reasonable_pool)
        
        # For sampling: if theoretical max is huge, sample more to ensure diversity
        if theoretical_max > 10000:
            # Sample a percentage based on difficulty
            sample_percentage = max(0.05, min(0.20, 0.10 * (1 + difficulty_score)))
            recommended_sample_size = int(theoretical_max * sample_percentage)
            recommended_sample_size = min(recommended_sample_size, 50000)
        else:
            # Use all combinations if feasible
            recommended_sample_size = theoretical_max
        
        return {
            "total_players": total_players,
            "num_teams": num_teams,
            "team_size": team_size,
            "players_per_combination": players_per_combination,
            "theoretical_max_combinations": theoretical_max,
            "difficulty_score": difficulty_score,
            "recommended_pool_size": recommended_pool_size,
            "recommended_sample_size": recommended_sample_size
        }

    def generate_balanced_teams(self, player_ids: List[int]) -> List[TeamCombination]:
        """Generate balanced teams from player IDs"""
        players = self.player_registry.get_players_by_ids(player_ids)
        self._validate_player_count(players)
        
        logger.info(f"Generating balanced teams for {len(players)} players across {self.config.num_teams} teams")
        
        # Analyze player pool BEFORE generating combinations to set optimal targets
        pool_analysis = self._analyze_player_pool(players)
        logger.info(f"Player pool analysis:")
        logger.info(f"  Total players: {pool_analysis['total_players']}")
        logger.info(f"  Theoretical max combinations: {pool_analysis['theoretical_max_combinations']}")
        logger.info(f"  Difficulty score: {pool_analysis['difficulty_score']:.2f} (0=easy, 1=hard)")
        logger.info(f"  Recommended pool size: {pool_analysis['recommended_pool_size']}")
        logger.info(f"  Recommended sample size: {pool_analysis['recommended_sample_size']}")
        
        valid_combinations = []
        
        # Generate team combinations based on analysis
        # If theoretical max is large, use recommended sample size
        if pool_analysis['theoretical_max_combinations'] > 50000:
            logger.info(f"Large combination space, using random sampling with {pool_analysis['recommended_sample_size']} samples")
            team_combinations = self._generate_random_team_combinations(
                players, self.config.num_teams, self.config.team_size,
                n_samples=pool_analysis['recommended_sample_size']
            )
        else:
            # Generate all combinations
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
        
        # Sort by balance score first (best balanced teams first)
        valid_combinations.sort(key=lambda x: x.balance.total_balance_score)
        
        # Apply diversity-first selection strategy to find at least 3 combinations
        min_required_combinations = max(3, self.config.top_n_teams)
        
        # Use recommended pool size from analysis
        target_pool_size = pool_analysis['recommended_pool_size']
        if len(valid_combinations) < target_pool_size:
            logger.info(f"Only {len(valid_combinations)} valid combinations found, generating more combinations (target: {target_pool_size})...")
            # Generate additional random combinations based on analysis
            n_samples_needed = target_pool_size - len(valid_combinations)
            # Use analysis to determine how many to sample (account for duplicates/invalid)
            sample_multiplier = 2 if pool_analysis['difficulty_score'] < 0.5 else 3
            max_samples = min(pool_analysis['recommended_sample_size'], 50000)
            additional_combinations = self._generate_random_team_combinations(
                players, self.config.num_teams, self.config.team_size, 
                n_samples=min(n_samples_needed * sample_multiplier, max_samples)
            )
            
            # Validate and add additional combinations
            added_count = 0
            for teams in additional_combinations:
                if len(valid_combinations) >= target_pool_size:
                    break
                if self._check_constraints(teams):
                    balance = self._calculate_team_balance(teams)
                    combination = TeamCombination(teams=teams, balance=balance)
                    # Avoid duplicates by checking if combination already exists
                    if not any(self._combinations_equal(combination, vc) for vc in valid_combinations):
                        valid_combinations.append(combination)
                        added_count += 1
            
            # Re-sort with new combinations
            valid_combinations.sort(key=lambda x: x.balance.total_balance_score)
            logger.info(f"Added {added_count} new combinations, now have {len(valid_combinations)} total valid combinations")
        
        # Use greedy diversity-first selection
        diverse_combinations = []
        # Adjust threshold based on difficulty - harder cases need more lenient threshold
        base_threshold = 1.0 - (self.config.diversity_threshold / 2.0)
        difficulty_adjusted_threshold = base_threshold * (1 - pool_analysis['difficulty_score'] * 0.5)
        min_diversity_score = max(0.05, difficulty_adjusted_threshold)
        
        logger.info(f"Using diversity threshold: {min_diversity_score:.3f} (adjusted for difficulty: {pool_analysis['difficulty_score']:.2f})")
        
        # First pass: Always include the best balanced combination
        if valid_combinations:
            diverse_combinations.append(valid_combinations[0])
        
        # Second pass: Greedily select combinations that maximize diversity
        # Adjust candidate pool size based on difficulty
        base_candidate_multiplier = 50
        difficulty_candidate_multiplier = base_candidate_multiplier * (1 + pool_analysis['difficulty_score'] * 4)
        candidate_pool_size = min(len(valid_combinations), int(min_required_combinations * difficulty_candidate_multiplier))
        candidates = valid_combinations[:candidate_pool_size]  # Top balanced candidates
        
        logger.info(f"Evaluating {candidate_pool_size} candidates for diversity...")
        
        rejected_count = 0
        rejected_too_many_repeats = 0
        rejected_low_diversity = 0
        
        for combination in candidates:
            if len(diverse_combinations) >= min_required_combinations:
                break
            
            # Skip if already selected
            if any(self._combinations_equal(combination, dc) for dc in diverse_combinations):
                continue
            
            diversity_score = self._calculate_team_diversity(combination, diverse_combinations, enforce_3_player_limit=True)
            
            # Accept if it meets diversity requirement (max 3 repeating players, diversity_score >= threshold)
            # Reject if diversity_score == -1.0 (more than 3 repeating players)
            if diversity_score == -1.0:
                # More than 3 repeating players, skip
                rejected_count += 1
                rejected_too_many_repeats += 1
                continue
            elif diversity_score < min_diversity_score:
                rejected_count += 1
                rejected_low_diversity += 1
                continue
            else:
                diverse_combinations.append(combination)
                logger.debug(f"Added combination {len(diverse_combinations)} with diversity score {diversity_score:.3f}")
        
        logger.info(f"Found {len(diverse_combinations)} diverse combinations after greedy selection (from {len(candidates)} candidates)")
        logger.info(f"Rejected {rejected_count} combinations: {rejected_too_many_repeats} with >3 repeats, {rejected_low_diversity} with low diversity score")
        
        # If still not enough, expand candidate pool significantly
        if len(diverse_combinations) < min_required_combinations:
            logger.info(f"Expanding search to find more diverse combinations...")
            # Try with much larger candidate pool
            larger_pool = min(len(valid_combinations), int(min_required_combinations * 200 * (1 + pool_analysis['difficulty_score'])))
            candidates = valid_combinations[:larger_pool]
            
            expanded_rejected_count = 0
            expanded_rejected_too_many_repeats = 0
            expanded_rejected_low_diversity = 0
            
            for combination in candidates:
                if len(diverse_combinations) >= min_required_combinations:
                    break
                
                # Skip if already selected
                if any(self._combinations_equal(combination, dc) for dc in diverse_combinations):
                    continue
                
                # Still enforce strict 3-player limit (no relaxed mode)
                diversity_score = self._calculate_team_diversity(combination, diverse_combinations, enforce_3_player_limit=True)
                # Accept if meets threshold
                if diversity_score == -1.0:
                    expanded_rejected_count += 1
                    expanded_rejected_too_many_repeats += 1
                    continue
                elif diversity_score < min_diversity_score:
                    expanded_rejected_count += 1
                    expanded_rejected_low_diversity += 1
                    continue
                else:
                    diverse_combinations.append(combination)
                    logger.debug(f"Added combination {len(diverse_combinations)} with diversity score {diversity_score:.3f}")
            
            logger.info(f"Expanded search: Rejected {expanded_rejected_count} combinations: {expanded_rejected_too_many_repeats} with >3 repeats, {expanded_rejected_low_diversity} with low diversity")
        
        logger.info(f"Final count: {len(diverse_combinations)} diverse combinations (checked up to {len(candidates)} candidates)")
        
        # If we still only have 1 combination, there might be a fundamental issue
        # Check if the problem is that all combinations use the same players
        if len(diverse_combinations) == 1 and len(valid_combinations) > 1:
            # Debug: Check what players are in the first combination vs others
            first_combo_players = set()
            for team in diverse_combinations[0].teams:
                first_combo_players.update(p.player_id for p in team)
            
            logger.warning(f"Only found 1 diverse combination. First combination uses {len(first_combo_players)} players: {sorted(first_combo_players)}")
            logger.warning(f"Total players available: {pool_analysis['total_players']}, Players per combination: {pool_analysis['players_per_combination']}")
            
            # Check if all combinations must use the same players (no leftover players)
            if pool_analysis['total_players'] == pool_analysis['players_per_combination']:
                logger.warning(f"⚠️ PROBLEM DETECTED: All combinations must use the same {pool_analysis['total_players']} players (no leftovers)")
                logger.warning(f"This means every combination shares all {pool_analysis['total_players']} players, violating the 3-player limit")
                logger.warning(f"Solution: We need to compare team-by-team overlap instead of overall player overlap")
                
                # Try team-by-team comparison as alternative
                logger.info("Attempting team-by-team diversity comparison instead...")
                for combo in valid_combinations[1:min(len(valid_combinations), 100)]:
                    if len(diverse_combinations) >= min_required_combinations:
                        break
                    
                    if any(self._combinations_equal(combo, dc) for dc in diverse_combinations):
                        continue
                    
                    # Use the same team-by-team comparison logic as _calculate_team_diversity
                    # Check if any team in new combo shares more than 3 players with any team in existing combos
                    max_team_overlap = 0
                    
                    new_team_sets = [set(p.player_id for p in team) for team in combo.teams]
                    
                    for existing_combo in diverse_combinations:
                        existing_team_sets = [set(p.player_id for p in team) for team in existing_combo.teams]
                        
                        # Check each team in new combo against each team in existing combo
                        for new_team in new_team_sets:
                            for existing_team in existing_team_sets:
                                overlap = len(new_team & existing_team)
                                max_team_overlap = max(max_team_overlap, overlap)
                    
                    # Accept if no individual team pair has more than 3 overlapping players
                    # This is the same logic as _calculate_team_diversity, so results should match
                    if max_team_overlap <= 3:
                        diverse_combinations.append(combo)
                        logger.info(f"Added combination {len(diverse_combinations)} using team-by-team comparison (max team overlap: {max_team_overlap})")
                    else:
                        logger.debug(f"Rejected combination: max team overlap {max_team_overlap} exceeds 3")
                
                logger.info(f"After team-by-team comparison: {len(diverse_combinations)} combinations found")
            else:
                # Check a few other combinations for debugging
                for i, combo in enumerate(valid_combinations[1:min(6, len(valid_combinations))], 1):
                    other_combo_players = set()
                    for team in combo.teams:
                        other_combo_players.update(p.player_id for p in team)
                    repeating = first_combo_players & other_combo_players
                    logger.warning(f"Combination {i+1} uses {len(other_combo_players)} players: {sorted(other_combo_players)}, repeats: {len(repeating)} players: {sorted(repeating)}")
                    
                    if len(repeating) > 3:
                        logger.warning(f"  -> This is why it was rejected: {len(repeating)} repeating players exceeds limit of 3")
        
        # Ensure we return at least 3, or as many as available
        result_count = min(min_required_combinations, len(diverse_combinations))
        if len(diverse_combinations) < 3:
            # Last resort: return what we have (may have more than 3 repeating players)
            result_count = len(diverse_combinations)
            if result_count == 0 and valid_combinations:
                # Absolute fallback: return top 3 balanced
                logger.warning("Could not find diverse combinations, returning top balanced ones")
                return valid_combinations[:min(3, len(valid_combinations))]
        
        return diverse_combinations[:result_count]

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
        must_be_on_same_teams=config.must_be_on_same_teams,
        must_be_on_same_teams_by_team=getattr(config, 'must_be_on_same_teams_by_team', {}),
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
