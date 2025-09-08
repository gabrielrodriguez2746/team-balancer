#!/usr/bin/env python3
"""
Data management for Team Balancer
Handles player data persistence and loading
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from team_balancer import Player, PlayerRegistry, Position, PlayerStats
from config import AppConfig
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """Manages player data persistence and loading"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.registry = PlayerRegistry()
    
    def save_players(self, players: List[Player]) -> None:
        """Save players to JSON file"""
        try:
            data = [player.to_dict() for player in players]
            with open(self.config.players_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(players)} players to {self.config.players_file}")
        except Exception as e:
            logger.error(f"Error saving players: {e}")
            raise
    
    def load_players(self) -> List[Player]:
        """Load players from JSON file"""
        try:
            if not self.config.players_file.exists():
                logger.warning(f"Players file not found: {self.config.players_file}")
                return []
            
            with open(self.config.players_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            players = []
            for player_data in data:
                try:
                    player = Player.from_dict(player_data)
                    players.append(player)
                except Exception as e:
                    logger.error(f"Error loading player {player_data.get('Name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"Loaded {len(players)} players from {self.config.players_file}")
            return players
        except Exception as e:
            logger.error(f"Error loading players: {e}")
            raise
    
    def load_players_to_registry(self) -> PlayerRegistry:
        """Load players into registry"""
        players = self.load_players()
        for player in players:
            self.registry.add_player(player)
        return self.registry
    
    def export_players_csv(self, output_file: Path) -> None:
        """Export players to CSV format"""
        try:
            import csv
            players = self.registry.get_all_players()
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow(['ID', 'Name', 'Positions', 'Level', 'Stamina', 'Speed'])
                
                # Data
                for player in players:
                    positions_str = ', '.join(pos.value for pos in player.positions)
                    writer.writerow([
                        player.player_id,
                        player.name,
                        positions_str,
                        player.stats.level,
                        player.stats.stamina,
                        player.stats.speed
                    ])
            
            logger.info(f"Exported {len(players)} players to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting players to CSV: {e}")
            raise
    
    def import_players_from_csv(self, csv_file: Path) -> List[Player]:
        """Import players from CSV format"""
        try:
            import csv
            players = []
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse positions
                        positions_str = row['Positions'].strip()
                        positions = [Position(pos.strip()) for pos in positions_str.split(',') if pos.strip()]
                        
                        # Create player
                        player = Player(
                            name=row['Name'].strip(),
                            positions=positions,
                            stats=PlayerStats(
                                level=float(row['Level']),
                                stamina=float(row['Stamina']),
                                speed=float(row['Speed'])
                            ),
                            player_id=int(row['ID']) if row['ID'] else None
                        )
                        players.append(player)
                    except Exception as e:
                        logger.error(f"Error parsing row {row}: {e}")
                        continue
            
            logger.info(f"Imported {len(players)} players from {csv_file}")
            return players
        except Exception as e:
            logger.error(f"Error importing players from CSV: {e}")
            raise
    
    def backup_players(self, backup_file: Optional[Path] = None) -> Path:
        """Create a backup of current players"""
        if backup_file is None:
            timestamp = Path().cwd().name
            backup_file = self.config.data_dir / f"players_backup_{timestamp}.json"
        
        players = self.registry.get_all_players()
        self.save_players(players)
        
        # Copy to backup location
        import shutil
        shutil.copy2(self.config.players_file, backup_file)
        logger.info(f"Created backup at {backup_file}")
        return backup_file
    
    def validate_player_data(self, players: List[Player]) -> List[str]:
        """Validate player data and return list of errors"""
        errors = []
        
        # Check for duplicate names
        names = [p.name for p in players]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate player names: {duplicates}")
        
        # Check for duplicate IDs
        ids = [p.player_id for p in players if p.player_id is not None]
        duplicate_ids = [pid for pid in set(ids) if ids.count(pid) > 1]
        if duplicate_ids:
            errors.append(f"Duplicate player IDs: {duplicate_ids}")
        
        # Check for invalid stats
        for player in players:
            try:
                # This will raise ValueError if stats are invalid
                _ = PlayerStats(
                    level=player.stats.level,
                    stamina=player.stats.stamina,
                    speed=player.stats.speed
                )
            except ValueError as e:
                errors.append(f"Invalid stats for {player.name}: {e}")
        
        return errors
    
    def get_player_statistics(self) -> Dict:
        """Get statistics about current players"""
        players = self.registry.get_all_players()
        
        if not players:
            return {"total_players": 0}
        
        # Position distribution
        position_counts = {}
        for player in players:
            for position in player.positions:
                position_counts[position.value] = position_counts.get(position.value, 0) + 1
        
        # Stat ranges
        levels = [p.stats.level for p in players]
        staminas = [p.stats.stamina for p in players]
        speeds = [p.stats.speed for p in players]
        
        return {
            "total_players": len(players),
            "position_distribution": position_counts,
            "level_stats": {
                "min": min(levels),
                "max": max(levels),
                "avg": sum(levels) / len(levels)
            },
            "stamina_stats": {
                "min": min(staminas),
                "max": max(staminas),
                "avg": sum(staminas) / len(staminas)
            },
            "speed_stats": {
                "min": min(speeds),
                "max": max(speeds),
                "avg": sum(speeds) / len(speeds)
            }
        } 