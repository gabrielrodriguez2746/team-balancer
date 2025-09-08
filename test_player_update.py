#!/usr/bin/env python3
"""
Test script to verify player update functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from team_balancer import Player, PlayerStats, Position, PlayerRegistry
from config import AppConfig
from data_manager import DataManager

def test_player_update():
    """Test the player update functionality"""
    print("🧪 Testing Player Update Functionality")
    print("=" * 50)
    
    # Initialize components
    config = AppConfig()
    data_manager = DataManager(config)
    registry = PlayerRegistry()
    
    # Load existing players
    players = data_manager.load_players()
    for player in players:
        registry.add_player(player)
    
    print(f"📋 Loaded {len(players)} players from registry")
    
    # Get a player to update
    all_players = registry.get_all_players()
    if not all_players:
        print("❌ No players found to test with")
        return False
    
    test_player = all_players[0]
    original_name = test_player.name
    original_level = test_player.stats.level
    
    print(f"🎯 Testing with player: {test_player.name} (ID: {test_player.player_id})")
    print(f"   Original name: {original_name}")
    print(f"   Original level: {original_level}")
    
    # Create updated player
    updated_stats = PlayerStats(
        level=original_level + 0.5,
        stamina=test_player.stats.stamina,
        speed=test_player.stats.speed
    )
    
    updated_player = Player(
        name=f"{original_name} (Updated)",
        positions=test_player.positions,
        stats=updated_stats,
        player_id=test_player.player_id
    )
    
    print(f"📝 Updating player...")
    print(f"   New name: {updated_player.name}")
    print(f"   New level: {updated_player.stats.level}")
    
    # Update the player
    try:
        success = registry.update_player(test_player.player_id, updated_player)
        if not success:
            print("❌ Failed to update player")
            return False
        
        print("✅ Player updated successfully in registry")
        
        # Verify the update
        updated_from_registry = registry.get_player(test_player.player_id)
        if not updated_from_registry:
            print("❌ Could not retrieve updated player from registry")
            return False
        
        print(f"🔍 Verification:")
        print(f"   Retrieved name: {updated_from_registry.name}")
        print(f"   Retrieved level: {updated_from_registry.stats.level}")
        
        if (updated_from_registry.name == updated_player.name and 
            updated_from_registry.stats.level == updated_player.stats.level):
            print("✅ Update verification successful!")
        else:
            print("❌ Update verification failed!")
            return False
        
        # Test name lookup
        player_by_name = registry.get_player_by_name(updated_player.name)
        if player_by_name and player_by_name.player_id == test_player.player_id:
            print("✅ Name lookup after update works correctly!")
        else:
            print("❌ Name lookup after update failed!")
            return False
        
        # Save to file
        all_players = registry.get_all_players()
        data_manager.save_players(all_players)
        print("✅ Changes saved to file successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during update: {e}")
        return False

def test_streamlit_update_simulation():
    """Simulate the Streamlit update process"""
    print("\n🖥️  Testing Streamlit Update Simulation")
    print("=" * 50)
    
    # Initialize components
    config = AppConfig()
    data_manager = DataManager(config)
    registry = PlayerRegistry()
    
    # Load existing players
    players = data_manager.load_players()
    for player in players:
        registry.add_player(player)
    
    # Get a player to simulate editing
    all_players = registry.get_all_players()
    if not all_players:
        print("❌ No players found to test with")
        return False
    
    test_player = all_players[0]
    print(f"🎯 Simulating edit for player: {test_player.name}")
    
    # Simulate form data
    new_name = f"{test_player.name} (Edited)"
    new_positions = ["MF", "FW"]  # Simulate new positions
    new_level = 4.5
    new_stamina = 3.8
    new_speed = 4.2
    
    print(f"📝 Form data:")
    print(f"   New name: {new_name}")
    print(f"   New positions: {new_positions}")
    print(f"   New stats: Level={new_level}, Stamina={new_stamina}, Speed={new_speed}")
    
    try:
        # Create new PlayerStats object (like in Streamlit)
        new_stats = PlayerStats(level=new_level, stamina=new_stamina, speed=new_speed)
        
        # Create updated player object (like in Streamlit)
        updated_player = Player(
            name=new_name,
            positions=[Position(pos) for pos in new_positions],
            stats=new_stats,
            player_id=test_player.player_id
        )
        
        # Update player in registry (like in Streamlit)
        success = registry.update_player(test_player.player_id, updated_player)
        if not success:
            print("❌ Failed to update player in registry")
            return False
        
        # Save to file (like in Streamlit)
        players = registry.get_all_players()
        data_manager.save_players(players)
        
        # Verify the update
        updated_from_registry = registry.get_player(test_player.player_id)
        if not updated_from_registry:
            print("❌ Could not retrieve updated player")
            return False
        
        print(f"✅ Streamlit simulation successful!")
        print(f"   Final name: {updated_from_registry.name}")
        print(f"   Final positions: {[pos.value for pos in updated_from_registry.positions]}")
        print(f"   Final stats: Level={updated_from_registry.stats.level}, "
              f"Stamina={updated_from_registry.stats.stamina}, "
              f"Speed={updated_from_registry.stats.speed}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during Streamlit simulation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Player Update Tests")
    print("=" * 60)
    
    # Test basic update functionality
    test1_success = test_player_update()
    
    # Test Streamlit simulation
    test2_success = test_streamlit_update_simulation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Basic Update Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Streamlit Simulation: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Player update functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1) 