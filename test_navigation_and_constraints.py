#!/usr/bin/env python3
"""
Test to verify navigation and constraint functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig, PlayerRegistry, Player, PlayerStats, Position
from config import AppConfig

def test_navigation_flow():
    """Test that the navigation flow works correctly"""
    print("🧪 Testing Navigation Flow...")
    
    # Test that the correct page methods exist
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        # Check that all required methods exist
        required_methods = [
            '_show_main_page',
            '_show_players_page', 
            '_show_create_teams_page',
            '_show_together_page',
            '_show_separate_page',
            '_show_results_page',
            '_generate_teams'
        ]
        
        for method_name in required_methods:
            if not hasattr(StreamlitTeamBalancerUI, method_name):
                print(f"❌ Missing method: {method_name}")
                return False
        
        print("✅ All navigation methods exist")
        return True
        
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
        return False

def test_per_team_constraints():
    """Test that per-team constraints work correctly"""
    print("\n🧪 Testing Per-Team Constraints...")
    
    # Create test configuration with per-team constraints
    config = TeamBalancerConfig(
        team_size=2,
        num_teams=2,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team={
            1: [[1, 2]],  # Players 1 and 2 must be on Team 1
            2: [[3, 4]]   # Players 3 and 4 must be on Team 2
        },
        stat_weights={'level': 1.0}
    )
    
    # Create player registry
    player_registry = PlayerRegistry()
    
    # Add test players
    test_players = [
        Player(name="Player1", positions=[Position.FW], stats=PlayerStats(level=3.0, stamina=3.5, speed=3.5), player_id=1),
        Player(name="Player2", positions=[Position.MF], stats=PlayerStats(level=3.5, stamina=3.8, speed=3.8), player_id=2),
        Player(name="Player3", positions=[Position.DF], stats=PlayerStats(level=4.0, stamina=3.0, speed=3.0), player_id=3),
        Player(name="Player4", positions=[Position.GK], stats=PlayerStats(level=2.5, stamina=2.5, speed=2.5), player_id=4)
    ]
    
    for player in test_players:
        player_registry.add_player(player)
    
    # Create TeamBalancer
    balancer = TeamBalancer(config, player_registry)
    
    try:
        # Generate teams
        player_ids = [1, 2, 3, 4]
        combinations = balancer.generate_balanced_teams(player_ids)
        
        print(f"✅ Generated {len(combinations)} team combinations")
        
        if combinations:
            # Check if constraints are respected in the first combination
            first_combination = combinations[0]
            teams = first_combination.teams
            
            # Check Team 1 constraints
            team1_player_ids = [p.player_id for p in teams[0]]
            team1_constraint_satisfied = all(pid in team1_player_ids for pid in [1, 2])
            
            # Check Team 2 constraints  
            team2_player_ids = [p.player_id for p in teams[1]]
            team2_constraint_satisfied = all(pid in team2_player_ids for pid in [3, 4])
            
            print(f"✅ Team 1 constraint satisfied: {team1_constraint_satisfied}")
            print(f"✅ Team 2 constraint satisfied: {team2_constraint_satisfied}")
            
            if team1_constraint_satisfied and team2_constraint_satisfied:
                print("🎉 Per-team constraints are working correctly!")
                return True
            else:
                print("❌ Per-team constraints are not being respected!")
                return False
        else:
            print("❌ No team combinations generated!")
            return False
            
    except Exception as e:
        print(f"❌ Per-team constraint test failed: {e}")
        return False

def test_ui_methods():
    """Test that UI methods are correctly implemented"""
    print("\n🧪 Testing UI Method Implementation...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        # Check that _show_together_page has the correct implementation
        import inspect
        source = inspect.getsource(StreamlitTeamBalancerUI._show_together_page)
        
        # Check for key elements of the per-team implementation
        required_elements = [
            "per_team_together_constraints",
            "team_tabs",
            "Team {i+1}",
            "must be on Team"
        ]
        
        for element in required_elements:
            if element not in source:
                print(f"❌ Missing element in _show_together_page: {element}")
                return False
        
        print("✅ _show_together_page has correct per-team implementation")
        return True
        
    except Exception as e:
        print(f"❌ UI method test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Navigation and Constraint Tests")
    print("=" * 60)
    
    success1 = test_navigation_flow()
    success2 = test_per_team_constraints()
    success3 = test_ui_methods()
    
    if success1 and success2 and success3:
        print("\n🎉 All tests passed! Navigation and constraints are working correctly.")
        print("\n📋 Summary:")
        print("✅ Navigation flow is properly implemented")
        print("✅ Per-team constraints are working")
        print("✅ UI methods are correctly implemented")
        print("✅ Application is ready for use")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
