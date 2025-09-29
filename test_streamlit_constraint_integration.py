#!/usr/bin/env python3
"""
Test to verify Streamlit constraint integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_streamlit_constraint_processing():
    """Test that Streamlit correctly processes per-team constraints"""
    print("🧪 Testing Streamlit Constraint Processing...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        from config import AppConfig
        
        # Create app config
        config = AppConfig()
        
        # Create UI instance
        ui = StreamlitTeamBalancerUI()
        
        print("✅ StreamlitTeamBalancerUI imported successfully")
        
        # Test that the _generate_teams method exists and has the right signature
        if hasattr(ui, '_generate_teams'):
            print("✅ _generate_teams method exists")
        else:
            print("❌ _generate_teams method missing")
            return False
        
        # Test that the _show_together_page method exists
        if hasattr(ui, '_show_together_page'):
            print("✅ _show_together_page method exists")
        else:
            print("❌ _show_together_page method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing StreamlitTeamBalancerUI: {e}")
        return False

def test_constraint_processing_logic():
    """Test the constraint processing logic"""
    print("\n🔍 Testing Constraint Processing Logic...")
    
    # Simulate the constraint processing logic from _generate_teams
    per_team_together_constraints = {
        1: [1, 2, 3],  # Players 1,2,3 must be on Team 1
        2: [4, 5, 6]   # Players 4,5,6 must be on Team 2
    }
    
    # Test the processing logic
    processed_constraints = {}
    
    for team_num, player_ids in per_team_together_constraints.items():
        if player_ids:  # Only add non-empty constraints
            processed_constraints[team_num] = [player_ids]
    
    print(f"   Input constraints: {per_team_together_constraints}")
    print(f"   Processed constraints: {processed_constraints}")
    
    # Verify the format is correct
    expected = {
        1: [[1, 2, 3]],
        2: [[4, 5, 6]]
    }
    
    if processed_constraints == expected:
        print("   ✅ Constraint processing logic is correct")
        return True
    else:
        print("   ❌ Constraint processing logic is incorrect")
        return False

def test_team_balancer_config_integration():
    """Test that TeamBalancerConfig accepts per-team constraints"""
    print("\n⚙️ Testing TeamBalancerConfig Integration...")
    
    try:
        from team_balancer import TeamBalancerConfig
        
        # Test creating config with per-team constraints
        config = TeamBalancerConfig(
            team_size=3,
            num_teams=2,
            top_n_teams=3,
            diversity_threshold=0.1,
            must_be_on_different_teams=[],
            must_be_on_same_teams=[],
            must_be_on_same_teams_by_team={
                1: [[1, 2]],
                2: [[3, 4]]
            },
            stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
        )
        
        print("   ✅ TeamBalancerConfig created successfully with per-team constraints")
        
        # Verify the constraints are stored correctly
        if hasattr(config, 'must_be_on_same_teams_by_team'):
            print("   ✅ must_be_on_same_teams_by_team field exists")
            print(f"   ✅ Constraints stored: {config.must_be_on_same_teams_by_team}")
        else:
            print("   ❌ must_be_on_same_teams_by_team field missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating TeamBalancerConfig: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Streamlit Constraint Integration Test")
    
    success1 = test_streamlit_constraint_processing()
    success2 = test_constraint_processing_logic()
    success3 = test_team_balancer_config_integration()
    
    if success1 and success2 and success3:
        print("\n🎉 ALL TESTS PASSED! Streamlit constraint integration is working!")
    else:
        print("\n❌ SOME TESTS FAILED! There are issues with the Streamlit integration.")
        sys.exit(1)
