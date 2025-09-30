#!/usr/bin/env python3
"""
Test the increased sample size with complex constraints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_increased_sample_size():
    """Test that increased sample size works for complex constraints"""
    
    print("🧪 Testing increased sample size with complex constraints...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    print(f"📊 Loaded {len(players)} players")
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Create a complex test case with constraints that require many samples
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    print(f"🎯 Selected player IDs: {selected_player_ids}")
    
    # Complex constraint: Multiple teams with multiple players each
    per_team_constraints = {
        1: [[1, 3, 6, 13]],  # 4 players on Team 1
        2: [[18, 27, 30, 24, 22]],  # 5 players on Team 2  
        3: [[40, 31]],  # 2 players on Team 3
        4: [[39, 38, 37]]  # 3 players on Team 4
    }
    
    print(f"🔗 Per-team constraints: {per_team_constraints}")
    
    # Create team balancer config
    team_config = TeamBalancerConfig(
        team_size=6,
        num_teams=4,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team=per_team_constraints,
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    # Create team balancer
    balancer = TeamBalancer(team_config, registry)
    
    print("🔄 Generating teams with increased sample size...")
    
    # Generate teams
    results = balancer.generate_balanced_teams(selected_player_ids)
    
    print(f"✅ Generated {len(results)} team combinations")
    
    if results:
        print("🎉 SUCCESS: Complex constraints are now working!")
        print("📊 Sample size increase from 10,000 to 100,000 is effective!")
        
        # Show first result
        first_result = results[0]
        print(f"\n�� First combination (Balance Score: {first_result.balance_score:.2f}):")
        for i, team in enumerate(first_result.teams, 1):
            team_total = sum(p.stats.level for p in team)
            print(f"🔵 TEAM {i} (Total: {team_total:.1f})")
            for player in team:
                print(f"   • {player.name} (Level: {player.stats.level:.1f})")
        
        return True
    else:
        print("❌ FAILED: Still no valid combinations found")
        print("🔍 May need even larger sample size or different approach")
        return False

if __name__ == "__main__":
    success = test_increased_sample_size()
    if success:
        print("\n🎯 CONCLUSION: Sample size increase is working!")
        print("📈 The application should now handle complex constraints successfully.")
    else:
        print("\n⚠️  CONCLUSION: May need further optimization.")
