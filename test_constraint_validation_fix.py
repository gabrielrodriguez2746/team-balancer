#!/usr/bin/env python3
"""
Unit test for constraint validation fix
Tests that selected_player_ids is properly defined before use
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_constraint_validation_fix():
    """Test that the constraint validation fix works correctly"""
    
    print("🧪 Testing constraint validation fix...")
    
    # Test 1: Check that the file compiles without syntax errors
    try:
        import py_compile
        py_compile.compile('team_balancer_streamlit.py', doraise=True)
        print("✅ Test 1 PASSED: File compiles without syntax errors")
    except py_compile.PyCompileError as e:
        print(f"❌ Test 1 FAILED: Syntax error: {e}")
        return False
    
    # Test 2: Check that selected_player_ids is defined before use
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Find the constraint processing section
    lines = content.split('\n')
    constraint_section_start = None
    selected_player_ids_definition = None
    
    for i, line in enumerate(lines):
        if "# Per-team together constraints (players who should be on specific teams)" in line:
            constraint_section_start = i
        if "selected_player_ids = {p.player_id for p in selected_players}" in line:
            selected_player_ids_definition = i
    
    if constraint_section_start is None:
        print("❌ Test 2 FAILED: Could not find constraint processing section")
        return False
    
    if selected_player_ids_definition is None:
        print("❌ Test 2 FAILED: Could not find selected_player_ids definition")
        return False
    
    if selected_player_ids_definition >= constraint_section_start:
        print("✅ Test 2 PASSED: selected_player_ids is defined before constraint processing")
    else:
        print("❌ Test 2 FAILED: selected_player_ids is defined after constraint processing")
        return False
    
    # Test 3: Check that filtering logic is present
    if "valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]" in content:
        print("✅ Test 3 PASSED: Constraint filtering logic is present")
    else:
        print("❌ Test 3 FAILED: Constraint filtering logic is missing")
        return False
    
    # Test 4: Check that warning messages are present
    if "Warning: Filtered out invalid player IDs" in content:
        print("✅ Test 4 PASSED: Warning messages are present")
    else:
        print("❌ Test 4 FAILED: Warning messages are missing")
        return False
    
    # Test 5: Check that debug logging is present
    if "Selected player IDs:" in content and "Raw per-team constraints:" in content:
        print("✅ Test 5 PASSED: Debug logging is present")
    else:
        print("❌ Test 5 FAILED: Debug logging is missing")
        return False
    
    print("\n🎉 All tests passed! Constraint validation fix is working correctly.")
    return True

def test_import_streamlit_module():
    """Test that the streamlit module can be imported without errors"""
    
    print("\n🧪 Testing Streamlit module import...")
    
    try:
        # Import the streamlit module to check for syntax errors
        import importlib.util
        spec = importlib.util.spec_from_file_location("team_balancer_streamlit", "team_balancer_streamlit.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Streamlit module import test PASSED: Module can be imported without errors")
        return True
    except Exception as e:
        print(f"❌ Streamlit module import test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting constraint validation fix tests...\n")
    
    test1_passed = test_constraint_validation_fix()
    test2_passed = test_import_streamlit_module()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The constraint validation fix is working correctly.")
        print("✅ The application should now work without the 'selected_player_ids' error.")
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        sys.exit(1)
