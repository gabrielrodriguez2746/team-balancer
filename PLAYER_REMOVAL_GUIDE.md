# 🗑️ Player Removal Guide

## Overview

This guide provides multiple ways to remove players that are no longer relevant from the Team Balancer system. The system now supports various removal methods with safety features like backups and confirmations.

## 🛠️ Tools Available

### 1. **Player Manager Script** (`player_manager.py`)
A comprehensive command-line tool for player management including removal operations.

### 2. **Interactive Mode**
A user-friendly interactive interface for player removal.

### 3. **Programmatic Removal**
Direct API calls for automated removal operations.

## 📋 Removal Methods

### **1. Remove by Player ID**
Remove a specific player using their unique ID.

```bash
# Remove player with ID 6
python player_manager.py --remove-id 6

# Remove player with ID 15
python player_manager.py --remove-id 15
```

### **2. Remove by Player Name**
Remove a player using their exact name.

```bash
# Remove player named "Edu"
python player_manager.py --remove-name "Edu"

# Remove player named "Victor Lopez"
python player_manager.py --remove-name "Victor Lopez"
```

### **3. Remove by Position**
Remove all players with a specific position.

```bash
# Remove all defenders (DF)
python player_manager.py --remove-position DF

# Remove all forwards (FW)
python player_manager.py --remove-position FW

# Remove all center midfielders (CM)
python player_manager.py --remove-position CM
```

### **4. Remove by Stats Threshold**
Remove players based on their performance statistics.

```bash
# Remove players with level below 2.0
python player_manager.py --remove-stats level:2.0:below

# Remove players with stamina above 4.5
python player_manager.py --remove-stats stamina:4.5:above

# Remove players with speed below 2.5
python player_manager.py --remove-stats speed:2.5:below
```

### **5. Remove Multiple Players by IDs**
Remove a list of specific players (useful for inactive players).

```bash
# Remove players with IDs 6, 12, 18
python player_manager.py --remove-ids "6,12,18"

# Remove players with IDs 1, 5, 10, 15, 20
python player_manager.py --remove-ids "1,5,10,15,20"
```

### **6. Interactive Removal Mode**
Use the interactive interface for guided removal.

```bash
python player_manager.py --interactive
```

This mode provides:
- List of all players with stats
- Menu-driven removal options
- Confirmation prompts
- Real-time feedback

## 🔒 Safety Features

### **Backup Before Removal**
Create a backup before performing removal operations.

```bash
# Create backup and remove player
python player_manager.py --backup --remove-id 6

# Create backup and remove by position
python player_manager.py --backup --remove-position DF
```

### **Confirmation Prompts**
All removal operations require confirmation (except single ID removal).

### **Validation**
- Checks if players exist before removal
- Validates position names and stat thresholds
- Reports invalid IDs or names

## 📊 List and Review Players

### **List All Players**
```bash
# Basic list
python player_manager.py --list

# List with stats
python player_manager.py --list-stats
```

### **Example Output**
```
📋 Found 41 players:
--------------------------------------------------------------------------------
ID  1: Cesar                | DF
ID  2: Lucas FC             | FW
ID  3: Nico Laderach        | DF
ID  4: Tomazzo              | LW
ID  5: Alexsandro           | CM
...
--------------------------------------------------------------------------------
```

## 🎯 Common Removal Scenarios

### **Scenario 1: Remove Inactive Players**
```bash
# List all players first
python player_manager.py --list-stats

# Remove specific inactive players
python player_manager.py --remove-ids "6,12,18,25,30"
```

### **Scenario 2: Remove Low-Performing Players**
```bash
# Remove players with level below 2.0
python player_manager.py --remove-stats level:2.0:below

# Remove players with stamina below 2.5
python player_manager.py --remove-stats stamina:2.5:below
```

### **Scenario 3: Remove Players by Position**
```bash
# Remove all goalkeepers (if any)
python player_manager.py --remove-position GK

# Remove all left wingers
python player_manager.py --remove-position LW
```

### **Scenario 4: Clean Up Duplicate Names**
```bash
# Remove specific player by name
python player_manager.py --remove-name "Victor Victor Victor"
```

## 🔧 Programmatic Removal

### **Using Python API**
```python
from player_manager import PlayerManager

# Initialize manager
manager = PlayerManager()

# Remove by ID
manager.remove_player_by_id(6)

# Remove by name
manager.remove_player_by_name("Edu")

# Remove by position
manager.remove_players_by_position("DF")

# Remove by stats
manager.remove_players_by_stats_threshold("level", 2.0, remove_below=True)

# Remove multiple players
manager.remove_inactive_players([6, 12, 18, 25])
```

### **Direct Registry Usage**
```python
from team_balancer import PlayerRegistry
from config import AppConfig
from data_manager import DataManager

# Setup
config = AppConfig()
data_manager = DataManager(config)
registry = PlayerRegistry()

# Load players
players = data_manager.load_players()
for player in players:
    registry.add_player(player)

# Remove player
registry.remove_player(6)

# Save changes
data_manager.save_players(registry.get_all_players())
```

## 📁 File Management

### **Backup Files**
Backups are stored in the `data/` directory with timestamps:
```
data/
├── players.json                    # Current players
├── config.json                     # Configuration
├── players_backup_1703123456.json  # Backup files
└── players_backup_1703123789.json
```

### **Restore from Backup**
```python
import shutil
from pathlib import Path

# Restore from backup
backup_file = Path("data/players_backup_1703123456.json")
current_file = Path("data/players.json")
shutil.copy(backup_file, current_file)
```

## ⚠️ Important Notes

### **ID Management**
- Player IDs are not reused after removal
- New players get the next available ID
- This prevents conflicts with team configurations

### **Team Generation Impact**
- Removing players may affect existing team configurations
- Update team generation scripts if they reference specific player IDs
- Check constraints in `config.json` for removed players

### **Data Integrity**
- Always create backups before bulk removal operations
- Verify the data after removal operations
- Test team generation after significant changes

## 🚀 Quick Start Examples

### **Remove a Single Player**
```bash
# 1. List players to find ID
python player_manager.py --list

# 2. Remove by ID
python player_manager.py --remove-id 6
```

### **Remove Low-Performing Players**
```bash
# 1. List with stats
python player_manager.py --list-stats

# 2. Remove players with level < 2.0
python player_manager.py --remove-stats level:2.0:below

# 3. Remove players with stamina < 2.5
python player_manager.py --remove-stats stamina:2.5:below
```

### **Remove Inactive Players**
```bash
# 1. Use interactive mode
python player_manager.py --interactive

# 2. Select option 5 (Remove multiple by IDs)
# 3. Enter IDs: 6,12,18,25,30
```

### **Clean Up by Position**
```bash
# Remove all left wingers
python player_manager.py --remove-position LW

# Remove all right wingers
python player_manager.py --remove-position RW
```

## 🔍 Verification

After removal operations, verify the changes:

```bash
# Check remaining players
python player_manager.py --list-stats

# Test team generation
python team_balancer.py

# Check data file
cat data/players.json | jq 'length'  # Count players
```

## 📞 Support

If you encounter issues:

1. **Check logs**: Look for error messages in the output
2. **Verify data**: Use `--list` to check current players
3. **Restore backup**: Use backup files if needed
4. **Test functionality**: Run team generation to ensure everything works

## 🎯 Best Practices

1. **Always backup** before bulk operations
2. **Review before removing** - use `--list-stats` first
3. **Remove in small batches** for better control
4. **Test after removal** - ensure team generation still works
5. **Update constraints** if removing players referenced in config
6. **Document changes** - keep track of removed players

---

**The player removal system provides flexible, safe, and efficient ways to manage your player database while maintaining data integrity and system functionality.** 