#!/usr/bin/env python3
"""
Unit test to verify DataFrame to Player ID mapping issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from data_manager import DataManager
from config import AppConfig

def test_dataframe_player_id_mapping():
    """Test the DataFrame to Player ID mapping issue"""
    
    print("🧪 Testing DataFrame to Player ID mapping...")
    
    # Load configuration and data
    config = AppConfig.load()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    print(f"📊 Total players loaded: {len(players)}")
    
    # Create DataFrame like in the UI
    player_data = []
    for player in players:
        player_data.append({
            'ID': player.player_id,
            'Name': player.name,
            'Level': player.stats.level,
            'Total': player.stats.level + player.stats.stamina + player.stats.speed
        })
    
    df = pd.DataFrame(player_data)
    
    print(f"📋 DataFrame created with {len(df)} rows")
    print(f"📋 DataFrame index range: {df.index.min()} to {df.index.max()}")
    print(f"📋 Player ID range: {df['ID'].min()} to {df['ID'].max()}")
    
    # Show first few rows
    print("\n📋 First 5 rows:")
    print(df.head())
    
    # Test the mapping issue
    print("\n🔍 Testing mapping issue:")
    for i in range(min(5, len(df))):
        row_index = df.index[i]
        player_id = df.iloc[i]['ID']
        player_name = df.iloc[i]['Name']
        print(f"   DataFrame index {row_index} → Player ID {player_id} ({player_name})")
    
    # Check if there's a mismatch
    index_range = set(df.index)
    id_range = set(df['ID'])
    
    print(f"\n🔍 Index range: {sorted(index_range)}")
    print(f"🔍 ID range: {sorted(id_range)}")
    
    if index_range == id_range:
        print("✅ No mapping issue detected")
        return True
    else:
        print("❌ MAPPING ISSUE DETECTED!")
        print(f"   DataFrame indices: {sorted(index_range)}")
        print(f"   Player IDs: {sorted(id_range)}")
        return False

if __name__ == "__main__":
    test_dataframe_player_id_mapping()
