#!/usr/bin/env python3
"""
Test constraint combinations to find the breaking point
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_constraint_combinations():
    """Test different constraint combinations to find the breaking point"""
    
    print("🔍 Testing constraint combinations...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    
    # Test different constraint combinations
    test_cases = [
        {
            "name": "Original failing case",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players on Team 1
                2: [[18, 27, 30, 24, 22]],  # 5 players on Team 2  
                3: [[40, 31]],  # 2 players on Team 3
                4: [[39, 38, 37]]  # 3 players on Team 4
            }
        },
        {
            "name": "Reduced Team 2 constraint",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players on Team 1
                2: [[18, 27, 30]],  # 3 players on Team 2 (reduced from 5)
                3: [[40, 31]],  # 2 players on Team 3
                4: [[39, 38, 37]]  # 3 players on Team 4
            }
        },
        {
            "name": "Only 2 teams with constraints",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players on Team 1
                2: [[18, 27, 30, 24, 22]]  # 5 players on Team 2
            }
        },
        {
            "name": "Only 3 teams with constraints",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players on Team 1
                2: [[18, 27, 30]],  # 3 players on Team 2
                3: [[40, 31]]  # 2 players on Team 3
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        
        # Calculate total constrained players
        total_constrained = sum(len(group[0]) for group in test_case['constraints'].values())
        print(f"📊 Total constrained players: {total_constrained}")
        
        team_config = TeamBalancerConfig(
            team_size=6,
            num_teams=4,
            top_n_teams=3,
            diversity_threshold=0.1,
            must_be_on_different_teams=[],
            must_be_on_same_teams=[],
            must_be_on_same_teams_by_team=test_case['constraints'],
            stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
        )
        
        balancer = TeamBalancer(team_config, registry)
        results = balancer.generate_balanced_teams(selected_player_ids)
        
        if results:
            print(f"✅ SUCCESS: {len(results)} combinations found")
        else:
            print(f"❌ FAILED: No combinations found")
            print(f"🔍 This constraint combination is mathematically impossible")

if __name__ == "__main__":
    test_constraint_combinations()
