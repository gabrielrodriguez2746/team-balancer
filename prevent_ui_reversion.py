#!/usr/bin/env python3
"""
Script to prevent UI reversion and ensure correct implementation
"""

import os
import re

def check_ui_implementation():
    """Check that the UI has the correct per-team implementation"""
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Check for key elements of the per-team implementation
    required_elements = [
        "per_team_together_constraints",
        "team_tabs = st.tabs",
        "Team {i+1}",
        "must be on Team",
        "st.session_state.per_team_together_constraints"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing elements: {missing_elements}")
        return False
    
    print("✅ UI implementation is correct")
    return True

def check_constraint_processing():
    """Check that constraint processing is implemented"""
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Check for constraint processing elements
    required_elements = [
        "per_team_together_constraints = {}",
        "must_be_on_same_teams_by_team=per_team_together_constraints",
        "Per-team together constraints:"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing constraint processing: {missing_elements}")
        return False
    
    print("✅ Constraint processing is implemented")
    return True

def check_navigation():
    """Check that navigation is correct"""
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Check for correct navigation
    if 'st.session_state.current_page = "together"' in content:
        print("❌ Found incorrect navigation (should be 'create_teams')")
        return False
    
    print("✅ Navigation is correct")
    return True

if __name__ == "__main__":
    print("🔍 Checking UI Implementation...")
    print("=" * 40)
    
    ui_ok = check_ui_implementation()
    constraint_ok = check_constraint_processing()
    nav_ok = check_navigation()
    
    if ui_ok and constraint_ok and nav_ok:
        print("\n🎉 All checks passed! UI is correctly implemented.")
    else:
        print("\n❌ Some checks failed. UI needs to be fixed.")
        exit(1)
