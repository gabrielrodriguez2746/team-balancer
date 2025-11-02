#!/usr/bin/env python3
"""
Data Initialization Script for Team Balancer
Creates the initial data files with default players or creates empty files
"""

import json
from pathlib import Path
from team_balancer import Player, PlayerStats, Position, PlayerRegistry
from config import AppConfig
from data_manager import DataManager

def create_default_players():
    """Create default players data"""
    return [
        {"Id": 1, "Name": "Cesar", "Position": ["DF"], "Stats": {"level": 3.5, "stamina": 3.2, "speed": 2.8}},
        {"Id": 2, "Name": "Lucas FC", "Position": ["FW"], "Stats": {"level": 3.8, "stamina": 3.5, "speed": 4.1}},
        {"Id": 3, "Name": "Nico Laderach", "Position": ["DF"], "Stats": {"level": 3.6, "stamina": 3.8, "speed": 3.0}},
        {"Id": 4, "Name": "Tomazzo", "Position": ["LW"], "Stats": {"level": 2.1, "stamina": 2.5, "speed": 3.8}},
        {"Id": 5, "Name": "Alexsandro", "Position": ["CM"], "Stats": {"level": 3.3, "stamina": 4.2, "speed": 3.1}},
        {"Id": 6, "Name": "Edu", "Position": ["DF"], "Stats": {"level": 1.0, "stamina": 1.5, "speed": 1.8}},
        {"Id": 7, "Name": "Sergio Borne", "Position": ["RW"], "Stats": {"level": 3.2, "stamina": 3.0, "speed": 3.9}},
        {"Id": 8, "Name": "Ale Masferrer", "Position": ["FW"], "Stats": {"level": 3.5, "stamina": 3.7, "speed": 3.6}},
        {"Id": 9, "Name": "Pablo", "Position": ["RW"], "Stats": {"level": 4.0, "stamina": 3.8, "speed": 4.3}},
        {"Id": 10, "Name": "Davide", "Position": ["FW", "CM"], "Stats": {"level": 4.0, "stamina": 4.1, "speed": 3.7}},
        {"Id": 11, "Name": "Gabo", "Position": ["CM"], "Stats": {"level": 4.0, "stamina": 4.5, "speed": 3.2}},
        {"Id": 12, "Name": "Shapi", "Position": ["RW"], "Stats": {"level": 1.8, "stamina": 2.2, "speed": 3.5}},
        {"Id": 13, "Name": "Leo", "Position": ["LW"], "Stats": {"level": 3.4, "stamina": 3.3, "speed": 3.8}},
        {"Id": 14, "Name": "Roger", "Position": ["DF"], "Stats": {"level": 3.7, "stamina": 4.0, "speed": 3.1}},
        {"Id": 15, "Name": "Fran", "Position": ["LW"], "Stats": {"level": 2.5, "stamina": 2.8, "speed": 3.4}},
        {"Id": 16, "Name": "Isra", "Position": ["RW"], "Stats": {"level": 2.2, "stamina": 2.5, "speed": 3.6}},
        {"Id": 17, "Name": "Luis", "Position": ["CM"], "Stats": {"level": 3.7, "stamina": 4.3, "speed": 3.0}},
        {"Id": 18, "Name": "Emmanuel", "Position": ["FW"], "Stats": {"level": 1.5, "stamina": 2.0, "speed": 2.8}},
        {"Id": 19, "Name": "Salta", "Position": ["FW", "CM"], "Stats": {"level": 4.0, "stamina": 4.2, "speed": 3.5}},
        {"Id": 20, "Name": "Juan Salamone", "Position": ["RW"], "Stats": {"level": 3.7, "stamina": 3.6, "speed": 4.0}},
        {"Id": 21, "Name": "Victor Victor Victor", "Position": ["DF"], "Stats": {"level": 3.0, "stamina": 3.4, "speed": 2.9}},
        {"Id": 22, "Name": "Amirhossein", "Position": ["FW"], "Stats": {"level": 2.8, "stamina": 3.1, "speed": 3.3}},
        {"Id": 23, "Name": "Victor Lopez", "Position": ["DF"], "Stats": {"level": 2.4, "stamina": 2.8, "speed": 2.5}},
        {"Id": 24, "Name": "Jose", "Position": ["RW"], "Stats": {"level": 3.8, "stamina": 3.5, "speed": 4.2}},
        {"Id": 25, "Name": "Diego", "Position": ["DF"], "Stats": {"level": 4.0, "stamina": 4.1, "speed": 3.3}},
        {"Id": 26, "Name": "Sergio Pino", "Position": ["RW"], "Stats": {"level": 2.8, "stamina": 2.9, "speed": 3.7}},
        {"Id": 27, "Name": "Peluk", "Position": ["CM"], "Stats": {"level": 4.0, "stamina": 4.4, "speed": 3.1}},
        {"Id": 28, "Name": "Checo", "Position": ["DF"], "Stats": {"level": 4.0, "stamina": 4.2, "speed": 3.4}},
        {"Id": 29, "Name": "Brian", "Position": ["RW", "DF"], "Stats": {"level": 3.3, "stamina": 3.8, "speed": 3.2}},
        {"Id": 30, "Name": "Lucho", "Position": ["FW", "CM"], "Stats": {"level": 4.0, "stamina": 4.0, "speed": 3.5}},
        {"Id": 31, "Name": "Jordi Capeta", "Position": ["CM"], "Stats": {"level": 4.5, "stamina": 4.6, "speed": 3.8}},
        {"Id": 32, "Name": "Royer", "Position": ["DF"], "Stats": {"level": 3.0, "stamina": 3.3, "speed": 2.7}},
        {"Id": 33, "Name": "Diyan", "Position": ["DF"], "Stats": {"level": 3.2, "stamina": 3.5, "speed": 2.9}},
        {"Id": 34, "Name": "Armen", "Position": ["DF"], "Stats": {"level": 3.7, "stamina": 3.9, "speed": 3.2}},
        {"Id": 35, "Name": "Damian", "Position": ["CM"], "Stats": {"level": 4.0, "stamina": 4.3, "speed": 3.4}},
        {"Id": 36, "Name": "Oscar Miercoles", "Position": ["DF"], "Stats": {"level": 3.0, "stamina": 3.2, "speed": 2.8}},
        {"Id": 37, "Name": "Oscar delantero", "Position": ["FW"], "Stats": {"level": 4.2, "stamina": 3.8, "speed": 4.1}},
        {"Id": 38, "Name": "Andres", "Position": ["DF"], "Stats": {"level": 3.0, "stamina": 3.4, "speed": 2.9}},
        {"Id": 39, "Name": "Erik", "Position": ["FW", "CM", "DF"], "Stats": {"level": 5.0, "stamina": 4.8, "speed": 4.5}},
        {"Id": 40, "Name": "Edu Ochoa", "Position": ["CM"], "Stats": {"level": 3.3, "stamina": 3.6, "speed": 3.0}},
        {"Id": 41, "Name": "Marc portero", "Position": ["DF"], "Stats": {"level": 4.0, "stamina": 4.1, "speed": 3.3}},
    ]

def initialize_data_directory():
    """Initialize the data directory with default data"""
    
    print("🔄 Initializing data directory...")
    
    # Setup
    config = AppConfig()
    data_manager = DataManager(config)
    
    # Create registry and add default players
    registry = PlayerRegistry()
    
    # Load default players
    for player_data in create_default_players():
        player = Player.from_dict(player_data)
        registry.add_player(player)
    
    # Get all players
    players = registry.get_all_players()
    
    # Save to JSON file
    data_manager.save_players(players)
    
    # Also save configuration
    config.save()
    
    print(f"✅ Created {config.players_file} with {len(players)} players")
    print(f"✅ Created {config.config_file}")
    
    # Show some statistics
    stats = data_manager.get_player_statistics(players)
    print(f"\n📊 Player Statistics:")
    print(f"   Total Players: {stats['total_players']}")
    print(f"   Average Level: {stats['level_stats']['avg']:.2f}")
    print(f"   Average Stamina: {stats['stamina_stats']['avg']:.2f}")
    print(f"   Average Speed: {stats['speed_stats']['avg']:.2f}")
    
    # Show position distribution
    print(f"\n🎯 Position Distribution:")
    for position, count in stats['position_distribution'].items():
        print(f"   {position}: {count} players")
    
    return players

def verify_data_files():
    """Verify that data files exist and are valid"""
    
    config = AppConfig()
    
    print("\n🔍 Verifying data files...")
    
    # Check players file
    if config.players_file.exists():
        print(f"✅ Players file exists: {config.players_file}")
        
        # Try to load and validate
        try:
            with open(config.players_file, 'r') as f:
                data = json.load(f)
            print(f"✅ Players file is valid JSON with {len(data)} players")
        except Exception as e:
            print(f"❌ Players file is invalid: {e}")
    else:
        print(f"❌ Players file missing: {config.players_file}")
    
    # Check config file
    if config.config_file.exists():
        print(f"✅ Config file exists: {config.config_file}")
        
        # Try to load and validate
        try:
            with open(config.config_file, 'r') as f:
                data = json.load(f)
            print(f"✅ Config file is valid JSON")
        except Exception as e:
            print(f"❌ Config file is invalid: {e}")
    else:
        print(f"❌ Config file missing: {config.config_file}")

def create_empty_data():
    """Create empty data files for a fresh start"""
    
    print("🔄 Creating empty data files...")
    
    # Setup
    config = AppConfig()
    data_manager = DataManager(config)
    
    # Create empty registry
    registry = PlayerRegistry()
    
    # Save empty players list
    data_manager.save_players([])
    
    # Save configuration
    config.save()
    
    print(f"✅ Created empty {config.players_file}")
    print(f"✅ Created {config.config_file}")
    print("\n💡 You can now add players using the UI or programmatically")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--empty":
        create_empty_data()
    else:
        # Initialize with default data
        players = initialize_data_directory()
        
        # Verify files
        verify_data_files()
        
        print("\n🎉 Data directory initialization complete!")
        print("\nYou can now:")
        print("1. Run 'python team_balancer.py' to use the new data system")
        print("2. Run 'python team_balancer_ui.py' to use the GUI")
        print("3. Add new players using the methods shown in the documentation")
        print("\nTo create empty data files instead, run: python initialize_data.py --empty")
