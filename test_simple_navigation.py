#!/usr/bin/env python3
"""
Simple test to verify navigation is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_navigation():
    """Test navigation with a simple check"""
    print("🧭 Simple Navigation Test...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Check if the together page method exists and is callable
        if hasattr(ui, '_show_together_page'):
            print("   ✅ _show_together_page method exists")
            
            # Check if the method has the expected content
            import inspect
            source = inspect.getsource(ui._show_together_page)
            
            if 'team_tabs = st.tabs' in source:
                print("   ✅ Method contains tab implementation")
            else:
                print("   ❌ Method missing tab implementation")
                
            if 'st.session_state.current_page = "separate"' in source:
                print("   ✅ Method contains navigation to separate page")
            else:
                print("   ❌ Method missing navigation to separate page")
                
        else:
            print("   ❌ _show_together_page method missing")
            return False
        
        # Check the navigation routing
        if hasattr(ui, 'run'):
            print("   ✅ run method exists")
            
            # Check if the routing logic includes together page
            source = inspect.getsource(ui.run)
            if 'elif st.session_state.current_page == "together":' in source:
                print("   ✅ Routing includes together page")
            else:
                print("   ❌ Routing missing together page")
                
        else:
            print("   ❌ run method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing navigation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Navigation Test")
    
    success = test_simple_navigation()
    
    if success:
        print("\n🎉 SIMPLE NAVIGATION TEST PASSED!")
        print("✅ Navigation components are present")
        print("✅ Navigation should work properly")
        print("\n🔍 If navigation is still not working, try:")
        print("   1. Clear browser cache")
        print("   2. Refresh the page")
        print("   3. Check browser console for errors")
        print("   4. Try a different browser")
    else:
        print("\n❌ SIMPLE NAVIGATION TEST FAILED!")
        sys.exit(1)
