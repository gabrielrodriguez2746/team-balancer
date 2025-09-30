#!/usr/bin/env python3
"""
Test the constraint checking logic directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_constraint_logic():
    """Test constraint checking logic directly"""
    
    print("�� Testing constraint checking logic directly...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    
    # Create a simple test case
    constraints = {1: [[1, 3, 6, 13]]}  # Just 4 players on Team 1
    
    team_config = TeamBalancerConfig(
        team_size=6,
        num_teams=4,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team=constraints,
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    balancer = TeamBalancer(team_config, registry)
    
    # Get the selected players
    selected_players = [registry.get_player_by_id(pid) for pid in selected_player_ids]
    
    print(f"📊 Selected players: {len(selected_players)}")
    print(f"🔗 Constraints: {constraints}")
    
    # Test the constraint checking logic manually
    print("\n🧪 Testing constraint checking manually...")
    
    # Create a valid team combination manually
    # Team 1: [1, 3, 6, 13, 5, 8] (4 constrained + 2 free)
    # Team 2: [9, 12, 18, 19, 21, 22]
    # Team 3: [24, 25, 27, 30, 31, 34]
    # Team 4: [35, 36, 37, 38, 39, 40]
    
    manual_teams = [
        [1, 3, 6, 13, 5, 8],      # Team 1: constrained players + 2 others
        [9, 12, 18, 19, 21, 22],  # Team 2
        [24, 25, 27, 30, 31, 34], # Team 3
        [35, 36, 37, 38, 39, 40]  # Team 4
    ]
    
    print(f"📊 Manual teams: {manual_teams}")
    
    # Check if this combination satisfies constraints
    team_ids_sets = [set(team) for team in manual_teams]
    
    # Test the constraint checking logic
    constraint_satisfied = True
    
    # Check must-be-same-on-specific-team constraints (1-based team index)
    if team_config.must_be_on_same_teams_by_team:
        for team_index_1_based, groups in team_config.must_be_on_same_teams_by_team.items():
            # Validate index points to an existing team
            if not (1 <= team_index_1_based <= len(team_ids_sets)):
                print(f"❌ Team index {team_index_1_based} is out of range")
                constraint_satisfied = False
                break
            
            team_ids = team_ids_sets[team_index_1_based - 1]
            print(f"🔍 Checking Team {team_index_1_based}: {team_ids}")
            
            for group in groups:
                print(f"🔍 Checking group {group} on Team {team_index_1_based}")
                if not all(pid in team_ids for pid in group):
                    print(f"❌ Group {group} not all in Team {team_index_1_based}")
                    constraint_satisfied = False
                    break
            
            if not constraint_satisfied:
                break
    
    if constraint_satisfied:
        print("✅ Manual constraint check PASSED")
    else:
        print("❌ Manual constraint check FAILED")
    
    # Now test with the actual team balancer
    print("\n🧪 Testing with actual team balancer...")
    results = balancer.generate_balanced_teams(selected_player_ids)
    print(f"📊 Team balancer results: {len(results)} combinations")

if __name__ == "__main__":
    test_constraint_logic()
