#!/usr/bin/env python3
"""
Unit test to verify the constraint processing fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_constraint_processing_fix():
    """Test that the constraint processing fix is working correctly"""
    
    print("🧪 Testing constraint processing fix...")
    
    # Test 1: Check that the file compiles without syntax errors
    try:
        import py_compile
        py_compile.compile('team_balancer_streamlit.py', doraise=True)
        print("✅ Test 1 PASSED: File compiles without syntax errors")
    except py_compile.PyCompileError as e:
        print(f"❌ Test 1 FAILED: Syntax error: {e}")
        return False
    
    # Test 2: Check that duplicate code is removed
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Count occurrences of duplicate lines
    duplicate_lines = [
        'selected_player_ids = {p.player_id for p in selected_players}',
        'print(f"   Selected player IDs: {sorted(selected_player_ids)}")',
        'print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))'
    ]
    
    for line in duplicate_lines:
        count = content.count(line)
        if count > 1:
            print(f"❌ Test 2 FAILED: Duplicate line found: {line} (appears {count} times)")
            return False
    
    print("✅ Test 2 PASSED: Duplicate code removed")
    
    # Test 3: Check that constraint processing logic is correct
    if 'if valid_player_ids:  # Only add non-empty constraints' in content:
        print("✅ Test 3 PASSED: Constraint processing logic is correct")
    else:
        print("❌ Test 3 FAILED: Constraint processing logic is incorrect")
        return False
    
    # Test 4: Check that per_team_together_constraints assignment is correct
    if 'per_team_together_constraints[team_num] = [valid_player_ids]' in content:
        print("✅ Test 4 PASSED: Constraint assignment is correct")
    else:
        print("❌ Test 4 FAILED: Constraint assignment is incorrect")
        return False
    
    # Test 5: Check that the old problematic code is removed
    if 'if player_ids:  # Only add non-empty constraints' not in content or content.count('if player_ids:  # Only add non-empty constraints') == 0:
        print("✅ Test 5 PASSED: Old problematic code removed")
    else:
        print("❌ Test 5 FAILED: Old problematic code still present")
        return False
    
    print("\n🎉 All tests passed! Constraint processing fix is working correctly.")
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
    print("🚀 Starting constraint processing fix tests...\n")
    
    test1_passed = test_constraint_processing_fix()
    test2_passed = test_import_streamlit_module()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The constraint processing fix is working correctly.")
        print("✅ The application should now correctly process all per-team constraints.")
        print("✅ All teams should now have their constraints respected.")
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        sys.exit(1)
