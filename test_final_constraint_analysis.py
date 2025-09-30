#!/usr/bin/env python3
"""
Final analysis of why complex constraints fail
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_final_constraint_analysis():
    """Final analysis of constraint failures"""
    
    print("🔍 Final constraint analysis...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    
    # Test progressive complexity
    test_cases = [
        {
            "name": "Single team constraint (4 players)",
            "constraints": {1: [[1, 3, 6, 13]]},
            "expected": "Should work"
        },
        {
            "name": "Two teams with constraints (4+3 players)",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players
                2: [[18, 27, 30]]    # 3 players
            },
            "expected": "Should work"
        },
        {
            "name": "Three teams with constraints (4+3+2 players)",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players
                2: [[18, 27, 30]],   # 3 players
                3: [[40, 31]]        # 2 players
            },
            "expected": "Should work"
        },
        {
            "name": "Four teams with constraints (4+3+2+3 players)",
            "constraints": {
                1: [[1, 3, 6, 13]],  # 4 players
                2: [[18, 27, 30]],   # 3 players
                3: [[40, 31]],       # 2 players
                4: [[39, 38, 37]]    # 3 players
            },
            "expected": "Should work"
        },
        {
            "name": "Four teams with constraints (4+5+2+3 players)",
            "constraints": {
                1: [[1, 3, 6, 13]],      # 4 players
                2: [[18, 27, 30, 24, 22]], # 5 players
                3: [[40, 31]],           # 2 players
                4: [[39, 38, 37]]        # 3 players
            },
            "expected": "May fail - very restrictive"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        
        # Calculate constraint info
        total_constrained = sum(len(group[0]) for group in test_case['constraints'].values())
        print(f"📊 Total constrained players: {total_constrained}/24")
        print(f"�� Remaining flexibility: {24 - total_constrained} players")
        
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
            print(f"📈 {test_case['expected']} ✓")
        else:
            print(f"❌ FAILED: No combinations found")
            print(f"📉 {test_case['expected']} ✗")
            
            # Calculate probability
            if total_constrained <= 12:
                print("🔍 This should be mathematically possible - investigating...")
            else:
                print("🔍 This may be too restrictive for random sampling")

if __name__ == "__main__":
    test_final_constraint_analysis()
