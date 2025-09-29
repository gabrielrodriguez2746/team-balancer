#!/usr/bin/env python3
"""
Test to validate constraint player IDs against selected players
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_constraint_validation():
    """Test constraint validation"""
    print("🔍 Testing Constraint Validation...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        
        ui = StreamlitTeamBalancerUI()
        
        # Get all players
        all_players = ui.player_registry.get_all_players()
        print(f"   Total players in registry: {len(all_players)}")
        
        # Show first few player IDs
        print("   First 10 player IDs:")
        for i, player in enumerate(all_players[:10]):
            print(f"     {i}: ID={player.player_id}, Name={player.name}")
        
        # Show last few player IDs
        print("   Last 10 player IDs:")
        for i, player in enumerate(all_players[-10:]):
            print(f"     {len(all_players)-10+i}: ID={player.player_id}, Name={player.name}")
        
        # Check if player IDs 40, 31, etc. exist
        high_ids = [40, 31, 39, 38, 37]
        print(f"   Checking high IDs: {high_ids}")
        for player_id in high_ids:
            player = ui.player_registry.get_player_by_id(player_id)
            if player:
                print(f"     ID {player_id}: EXISTS - {player.name}")
            else:
                print(f"     ID {player_id}: NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing constraint validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Constraint Validation Test")
    
    success = test_constraint_validation()
    
    if success:
        print("\n🎉 CONSTRAINT VALIDATION TEST COMPLETE!")
    else:
        print("\n❌ CONSTRAINT VALIDATION TEST FAILED!")
        sys.exit(1)
