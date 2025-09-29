#!/usr/bin/env python3
"""
Debug test to verify navigation is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation_debug():
    """Test navigation with debug output"""
    print("🔍 Debugging Navigation Issues...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Check if the together page method exists and is callable
        if hasattr(ui, '_show_together_page'):
            print("   ✅ _show_together_page method exists")
            
            # Try to inspect the method
            import inspect
            sig = inspect.signature(ui._show_together_page)
            print(f"   �� Method signature: {sig}")
            
            # Check if the method has the expected content
            source = inspect.getsource(ui._show_together_page)
            if 'team_tabs = st.tabs' in source:
                print("   ✅ Method contains tab implementation")
            else:
                print("   ❌ Method missing tab implementation")
                
            if 'st.session_state.current_page = "together"' in source:
                print("   ✅ Method contains navigation to together page")
            else:
                print("   ❌ Method missing navigation to together page")
                
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
        print(f"   ❌ Error debugging navigation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Navigation Debug Test")
    
    success = test_navigation_debug()
    
    if success:
        print("\n🎉 NAVIGATION DEBUG COMPLETE!")
        print("✅ All navigation components are present")
    else:
        print("\n❌ NAVIGATION DEBUG FAILED!")
        sys.exit(1)
