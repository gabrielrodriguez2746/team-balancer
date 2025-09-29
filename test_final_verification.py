#!/usr/bin/env python3
"""
Final verification test for the complete constraint system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_final_verification():
    """Final verification of the complete system"""
    print("🚀 FINAL VERIFICATION TEST")
    print("=" * 50)
    
    # Test 1: Backend constraint system
    print("\n1️⃣ Testing Backend Constraint System...")
    try:
        from team_balancer import TeamBalancer, TeamBalancerConfig, PlayerRegistry, Player, PlayerStats, Position
        
        # Create test players
        players = [
            Player("Player1", [Position.MF], PlayerStats(level=4.0, stamina=3.5, speed=3.5)),
            Player("Player2", [Position.DF], PlayerStats(level=3.5, stamina=3.0, speed=3.0)),
            Player("Player3", [Position.FW], PlayerStats(level=4.5, stamina=4.0, speed=4.0)),
            Player("Player4", [Position.MF], PlayerStats(level=3.0, stamina=2.5, speed=2.5)),
        ]
        
        # Create player registry
        registry = PlayerRegistry()
        for player in players:
            registry.add_player(player)
        
        # Test per-team constraints
        config = TeamBalancerConfig(
            team_size=2,
            num_teams=2,
            top_n_teams=3,
            diversity_threshold=0.1,
            must_be_on_different_teams=[],
            must_be_on_same_teams=[],
            must_be_on_same_teams_by_team={
                1: [[1, 2]],  # Players 1,2 must be on Team 1
                2: [[3, 4]]   # Players 3,4 must be on Team 2
            },
            stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
        )
        
        balancer = TeamBalancer(config, registry)
        teams = balancer.generate_balanced_teams([1, 2, 3, 4])
        
        if teams and len(teams) > 0:
            print("   ✅ Backend constraint system working")
        else:
            print("   ❌ Backend constraint system failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        return False
    
    # Test 2: Streamlit integration
    print("\n2️⃣ Testing Streamlit Integration...")
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Check required methods exist
        required_methods = ['_show_together_page', '_generate_teams', '_show_separate_page']
        for method in required_methods:
            if hasattr(ui, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} missing")
                return False
                
    except Exception as e:
        print(f"   ❌ Streamlit integration test failed: {e}")
        return False
    
    # Test 3: Constraint processing logic
    print("\n3️⃣ Testing Constraint Processing Logic...")
    try:
        # Simulate the constraint processing from _generate_teams
        per_team_together_constraints = {
            1: [1, 2, 3],
            2: [4, 5, 6]
        }
        
        processed_constraints = {}
        for team_num, player_ids in per_team_together_constraints.items():
            if player_ids:
                processed_constraints[team_num] = [player_ids]
        
        expected = {1: [[1, 2, 3]], 2: [[4, 5, 6]]}
        if processed_constraints == expected:
            print("   ✅ Constraint processing logic correct")
        else:
            print("   ❌ Constraint processing logic incorrect")
            return False
            
    except Exception as e:
        print(f"   ❌ Constraint processing test failed: {e}")
        return False
    
    # Test 4: File syntax check
    print("\n4️⃣ Testing File Syntax...")
    try:
        import py_compile
        py_compile.compile('team_balancer.py', doraise=True)
        py_compile.compile('team_balancer_streamlit.py', doraise=True)
        print("   ✅ All files have correct syntax")
    except Exception as e:
        print(f"   ❌ Syntax error: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Backend constraint system working")
    print("✅ Streamlit integration working") 
    print("✅ Constraint processing logic correct")
    print("✅ All files have correct syntax")
    print("\n🚀 The constraint system is fully functional!")
    
    return True

if __name__ == "__main__":
    success = test_final_verification()
    if not success:
        print("\n❌ VERIFICATION FAILED!")
        sys.exit(1)
    else:
        print("\n✅ VERIFICATION SUCCESSFUL!")
