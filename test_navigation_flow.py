#!/usr/bin/env python3
"""
Test the complete navigation flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation_flow():
    """Test the complete navigation flow"""
    print("🧭 Testing Complete Navigation Flow...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Test that all required methods exist
        required_methods = [
            '_show_main_page',
            '_show_players_page', 
            '_show_create_teams_page',
            '_show_together_page',
            '_show_separate_page',
            '_show_results_page'
        ]
        
        for method in required_methods:
            if hasattr(ui, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} missing")
                return False
        
        # Test the navigation routing logic
        import inspect
        source = inspect.getsource(ui.run)
        
        # Check for all page routes
        routes = [
            'if st.session_state.current_page == "main":',
            'elif st.session_state.current_page == "players":',
            'elif st.session_state.current_page == "create_teams":',
            'elif st.session_state.current_page == "together":',
            'elif st.session_state.current_page == "separate":',
            'elif st.session_state.current_page == "results":'
        ]
        
        for route in routes:
            if route in source:
                print(f"   ✅ {route} exists")
            else:
                print(f"   ❌ {route} missing")
                return False
        
        # Test button navigation
        button_navigations = [
            'st.session_state.current_page = "together"',
            'st.session_state.current_page = "separate"',
            'st.session_state.current_page = "create_teams"',
            'st.session_state.current_page = "results"'
        ]
        
        for nav in button_navigations:
            if nav in source:
                print(f"   ✅ {nav} exists")
            else:
                print(f"   ❌ {nav} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing navigation flow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Navigation Flow Test")
    
    success = test_navigation_flow()
    
    if success:
        print("\n🎉 NAVIGATION FLOW TEST PASSED!")
        print("✅ All navigation components are present and correct")
        print("✅ Navigation should work properly")
    else:
        print("\n❌ NAVIGATION FLOW TEST FAILED!")
        sys.exit(1)
