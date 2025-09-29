#!/usr/bin/env python3
"""
Test DataFrame creation in the together page
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dataframe_creation():
    """Test DataFrame creation"""
    print("🔍 Testing DataFrame Creation...")
    
    try:
        from team_balancer_streamlit import StreamlitTeamBalancerUI
        import pandas as pd
        
        ui = StreamlitTeamBalancerUI()
        
        # Simulate selected players (first 24 players)
        all_players = ui.player_registry.get_all_players()
        selected_players = all_players[:24]  # First 24 players
        
        print(f"   Selected players: {len(selected_players)}")
        print("   Selected player IDs:")
        for player in selected_players:
            print(f"     ID={player.player_id}, Name={player.name}")
        
        # Create DataFrame like in the together page
        player_data = []
        for player in selected_players:
            player_data.append({
                'ID': player.player_id,
                'Name': player.name,
                'Positions': ', '.join([pos.value for pos in player.positions]),
                'Level': player.stats.level,
                'Stamina': player.stats.stamina,
                'Speed': player.stats.speed,
                'Total': player.stats.level + player.stats.stamina + player.stats.speed
            })
        
        df = pd.DataFrame(player_data)
        
        print(f"\n   DataFrame shape: {df.shape}")
        print("   DataFrame index range:", df.index.min(), "to", df.index.max())
        print("   DataFrame ID range:", df['ID'].min(), "to", df['ID'].max())
        
        # Test the multiselect logic
        print("\n   Testing multiselect logic:")
        for i in df.index:
            player_id = df.iloc[i]['ID']
            print(f"     Index {i} -> Player ID {player_id} ({df.iloc[i]['Name']})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing DataFrame creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting DataFrame Creation Test")
    
    success = test_dataframe_creation()
    
    if success:
        print("\n🎉 DATAFRAME CREATION TEST COMPLETE!")
    else:
        print("\n❌ DATAFRAME CREATION TEST FAILED!")
        sys.exit(1)
