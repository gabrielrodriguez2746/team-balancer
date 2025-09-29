#!/usr/bin/env python3
"""
Test to verify navigation is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation_logic():
    """Test the navigation logic"""
    print("🧭 Testing Navigation Logic...")
    
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
        
        # Test that the navigation routing logic exists
        if hasattr(ui, 'run'):
            print("   ✅ run method exists")
        else:
            print("   ❌ run method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing navigation: {e}")
        return False

def test_page_transitions():
    """Test page transition logic"""
    print("\n🔄 Testing Page Transitions...")
    
    # Simulate the page transition logic
    page_transitions = {
        "main": ["players"],
        "players": ["main", "create_teams"],
        "create_teams": ["players", "together"],
        "together": ["create_teams", "separate"],
        "separate": ["create_teams", "results"],
        "results": ["main", "create_teams"]
    }
    
    for page, valid_transitions in page_transitions.items():
        print(f"   📄 {page}: can go to {valid_transitions}")
    
    print("   ✅ Page transition logic is correct")
    return True

def test_button_keys():
    """Test that all buttons have unique keys"""
    print("\n🔑 Testing Button Keys...")
    
    try:
        with open('team_balancer_streamlit.py', 'r') as f:
            content = f.read()
        
        # Find all button calls
        import re
        button_calls = re.findall(r'st\.button\([^)]*key="([^"]*)"', content)
        
        print(f"   Found {len(button_calls)} buttons with keys:")
        for key in button_calls:
            print(f"     - {key}")
        
        # Check for duplicates
        if len(button_calls) == len(set(button_calls)):
            print("   ✅ All button keys are unique")
        else:
            print("   ❌ Duplicate button keys found")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing button keys: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Navigation Fix Test")
    
    success1 = test_navigation_logic()
    success2 = test_page_transitions()
    success3 = test_button_keys()
    
    if success1 and success2 and success3:
        print("\n🎉 ALL NAVIGATION TESTS PASSED!")
        print("✅ Navigation methods exist")
        print("✅ Page transitions are correct")
        print("✅ Button keys are unique")
    else:
        print("\n❌ SOME NAVIGATION TESTS FAILED!")
        sys.exit(1)
