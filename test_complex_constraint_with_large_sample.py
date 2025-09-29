#!/usr/bin/env python3
"""
Test complex constraint with increased sample size
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_complex_constraint():
    """Test complex constraint with increased sample size"""
    
    print("🧪 Testing complex constraint with increased sample size...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    print(f"📊 Loaded {len(players)} players")
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Create a simple test case
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    print(f"🎯 Selected player IDs: {selected_player_ids}")
    
    # Test constraint: Team 1 should have players [30, 27, 24, 22, 18] (5 players)
    per_team_constraints = {1: [[30, 27, 24, 22, 18]]}
    print(f"🔗 Per-team constraints: {per_team_constraints}")
    
    # Create config
    config = TeamBalancerConfig(
        team_size=6,
        num_teams=4,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team=per_team_constraints,
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    # Create balancer
    balancer = TeamBalancer(config, registry)
    
    # Get selected players
    selected_players = [p for p in players if p.player_id in selected_player_ids]
    print(f"📋 Selected players: {len(selected_players)}")
    
    # Test team generation
    print(f"🔄 Starting team generation with increased sample size...")
    try:
        combinations = balancer.generate_balanced_teams(selected_player_ids)
        print(f"✅ Generated {len(combinations)} combinations")
        
        if combinations:
            print(f"🏆 First combination:")
            for i, team in enumerate(combinations[0].teams):
                print(f"   Team {i+1}: {[p.player_id for p in team]}")
                
            # Verify constraint satisfaction
            team1_ids = [p.player_id for p in combinations[0].teams[0]]
            constraint_players = [30, 27, 24, 22, 18]
            if all(pid in team1_ids for pid in constraint_players):
                print(f"✅ Constraint satisfied: All required players {constraint_players} are in Team 1")
            else:
                missing = [pid for pid in constraint_players if pid not in team1_ids]
                print(f"❌ Constraint not satisfied: Missing players {missing} from Team 1")
        else:
            print(f"❌ No combinations found!")
            
    except Exception as e:
        print(f"❌ Error during team generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complex_constraint()
