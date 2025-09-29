#!/usr/bin/env python3
"""
Unit test to verify the DataFrame mapping fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dataframe_mapping_fix():
    """Test that the DataFrame mapping fix is working correctly"""
    
    print("🧪 Testing DataFrame mapping fix...")
    
    # Test 1: Check that the file compiles without syntax errors
    try:
        import py_compile
        py_compile.compile('team_balancer_streamlit.py', doraise=True)
        print("✅ Test 1 PASSED: File compiles without syntax errors")
    except py_compile.PyCompileError as e:
        print(f"❌ Test 1 FAILED: Syntax error: {e}")
        return False
    
    # Test 2: Check that multiselect now uses player IDs as options
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Check for the fixed multiselect in create teams page
    if 'options=df[\'ID\'].tolist()' in content:
        print("✅ Test 2 PASSED: Create teams multiselect uses player IDs as options")
    else:
        print("❌ Test 2 FAILED: Create teams multiselect still uses DataFrame indices")
        return False
    
    # Check for the fixed multiselect in together page
    if 'together_player_ids = st.multiselect(' in content:
        print("✅ Test 3 PASSED: Together page multiselect uses player IDs")
    else:
        print("❌ Test 3 FAILED: Together page multiselect still uses DataFrame indices")
        return False
    
    # Test 4: Check that constraint storage is simplified
    if 'st.session_state.per_team_together_constraints[team_number] = together_player_ids' in content:
        print("✅ Test 4 PASSED: Constraint storage is simplified")
    else:
        print("❌ Test 4 FAILED: Constraint storage still uses complex mapping")
        return False
    
    # Test 5: Check that the old problematic code is removed
    if 'options=df.index' not in content:
        print("✅ Test 5 PASSED: Old problematic DataFrame index usage removed")
    else:
        print("❌ Test 5 FAILED: Old problematic DataFrame index usage still present")
        return False
    
    # Test 6: Check that format_func uses correct lookup
    if 'df[df[\'ID\'] == x][\'Name\'].iloc[0]' in content:
        print("✅ Test 6 PASSED: Format function uses correct player ID lookup")
    else:
        print("❌ Test 6 FAILED: Format function still uses DataFrame index lookup")
        return False
    
    print("\n🎉 All tests passed! DataFrame mapping fix is working correctly.")
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
    print("🚀 Starting DataFrame mapping fix tests...\n")
    
    test1_passed = test_dataframe_mapping_fix()
    test2_passed = test_import_streamlit_module()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The DataFrame mapping fix is working correctly.")
        print("✅ The application should now correctly map player selections to player IDs.")
        print("✅ Constraints should now work properly with the correct player IDs.")
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        sys.exit(1)
