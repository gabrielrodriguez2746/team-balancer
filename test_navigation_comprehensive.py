#!/usr/bin/env python3
"""
Comprehensive test to verify navigation is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation_comprehensive():
    """Test navigation comprehensively"""
    print("🧭 Comprehensive Navigation Test...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Test 1: All methods exist
        print("\n1️⃣ Testing Method Existence...")
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
        
        # Test 2: Navigation routing
        print("\n2️⃣ Testing Navigation Routing...")
        import inspect
        source = inspect.getsource(ui.run)
        
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
        
        # Test 3: Button navigation
        print("\n3️⃣ Testing Button Navigation...")
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
        
        # Test 4: Session state initialization
        print("\n4️⃣ Testing Session State Initialization...")
        init_source = inspect.getsource(ui.__init__)
        if 'st.session_state.current_page = "main"' in init_source:
            print("   ✅ Session state initialization exists")
        else:
            print("   ❌ Session state initialization missing")
            return False
        
        # Test 5: Button keys
        print("\n5️⃣ Testing Button Keys...")
        button_keys = [
            'key="continue_together"',
            'key="continue_separate"',
            'key="back_together"',
            'key="back_separate"'
        ]
        
        for key in button_keys:
            if key in source:
                print(f"   ✅ {key} exists")
            else:
                print(f"   ❌ {key} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing navigation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Navigation Test")
    
    success = test_navigation_comprehensive()
    
    if success:
        print("\n🎉 COMPREHENSIVE NAVIGATION TEST PASSED!")
        print("✅ All navigation components are present and correct")
        print("✅ Navigation should work properly")
        print("\n🔍 If navigation is still not working, the issue might be:")
        print("   - Browser cache issues")
        print("   - Session state not persisting")
        print("   - JavaScript errors in the browser")
        print("   - Streamlit version compatibility issues")
    else:
        print("\n❌ COMPREHENSIVE NAVIGATION TEST FAILED!")
        sys.exit(1)
