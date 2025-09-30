#!/usr/bin/env python3
"""
Detailed debug of constraint checking logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_constraint_debug_detailed():
    """Debug constraint checking in detail"""
    
    print("🔍 Detailed constraint debugging...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Test with a simple constraint first
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    
    print(f"🎯 Selected player IDs: {selected_player_ids}")
    print(f"📊 Total players: {len(selected_player_ids)}")
    print(f"🎯 Team size: 6, Teams: 4")
    print(f"📊 Total needed: {6 * 4} = 24 players")
    
    # Test 1: Simple constraint (2 players on same team)
    print("\n🧪 TEST 1: Simple constraint (2 players on Team 1)")
    simple_constraints = {1: [[1, 3]]}
    
    team_config = TeamBalancerConfig(
        team_size=6,
        num_teams=4,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team=simple_constraints,
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    balancer = TeamBalancer(team_config, registry)
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"✅ Simple constraint result: {len(results)} combinations")
    
    # Test 2: Medium constraint (3 players on same team)
    print("\n🧪 TEST 2: Medium constraint (3 players on Team 1)")
    medium_constraints = {1: [[1, 3, 6]]}
    
    team_config.must_be_on_same_teams_by_team = medium_constraints
    balancer = TeamBalancer(team_config, registry)
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"✅ Medium constraint result: {len(results)} combinations")
    
    # Test 3: Complex constraint (4 players on same team)
    print("\n🧪 TEST 3: Complex constraint (4 players on Team 1)")
    complex_constraints = {1: [[1, 3, 6, 13]]}
    
    team_config.must_be_on_same_teams_by_team = complex_constraints
    balancer = TeamBalancer(team_config, registry)
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"✅ Complex constraint result: {len(results)} combinations")
    
    # Test 4: Very complex constraint (5 players on same team)
    print("\n🧪 TEST 4: Very complex constraint (5 players on Team 1)")
    very_complex_constraints = {1: [[1, 3, 6, 13, 18]]}
    
    team_config.must_be_on_same_teams_by_team = very_complex_constraints
    balancer = TeamBalancer(team_config, registry)
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"✅ Very complex constraint result: {len(results)} combinations")
    
    # Test 5: Multiple teams with constraints
    print("\n�� TEST 5: Multiple teams with constraints")
    multi_team_constraints = {
        1: [[1, 3]],  # 2 players on Team 1
        2: [[6, 13]]  # 2 players on Team 2
    }
    
    team_config.must_be_on_same_teams_by_team = multi_team_constraints
    balancer = TeamBalancer(team_config, registry)
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"✅ Multi-team constraint result: {len(results)} combinations")
    
    print("\n📊 SUMMARY:")
    print("This will help identify at what point constraints become impossible")

if __name__ == "__main__":
    test_constraint_debug_detailed()
