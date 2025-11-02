#!/usr/bin/env python3
"""
Player Management Script for Team Balancer
Provides tools to add, remove, and manage players
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from team_balancer import Player, PlayerStats, Position, PlayerRegistry
from config import AppConfig
from data_manager import DataManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PlayerManager:
    """Manages player operations including removal"""
    
    def __init__(self):
        self.config = AppConfig()
        self.data_manager = DataManager(self.config)
        self.registry = PlayerRegistry()
        
        # Load existing players
        players = self.data_manager.load_players()
        for player in players:
            self.registry.add_player(player)
    
    def list_players(self, show_stats: bool = False) -> None:
        """List all players with optional stats"""
        players = self.registry.get_all_players()
        
        if not players:
            print("No players found.")
            return
        
        print(f"\n📋 Found {len(players)} players:")
        print("-" * 80)
        
        for player in sorted(players, key=lambda p: p.player_id):
            positions_str = ", ".join(pos.value for pos in player.positions)
            if show_stats:
                print(f"ID {player.player_id:2d}: {player.name:<20} | {positions_str:<15} | "
                      f"Level: {player.stats.level:.1f} | Stamina: {player.stats.stamina:.1f} | "
                      f"Speed: {player.stats.speed:.1f}")
            else:
                print(f"ID {player.player_id:2d}: {player.name:<20} | {positions_str}")
        
        print("-" * 80)
    
    def _remove_player(self, player: Player) -> bool:
        """Internal helper to remove a player"""
        player_id = player.player_id
        player_name = player.name
        self.registry.remove_player(player_id)
        self._save_changes()
        logger.info(f"✅ Removed player: {player_name} (ID: {player_id})")
        return True
    
    def remove_player_by_id(self, player_id: int) -> bool:
        """Remove a player by ID"""
        player = self.registry.get_player(player_id)
        if not player:
            logger.error(f"Player with ID {player_id} not found")
            return False
        return self._remove_player(player)
    
    def remove_player_by_name(self, name: str) -> bool:
        """Remove a player by name (exact match)"""
        player = self.registry.get_player_by_name(name)
        if not player:
            logger.error(f"Player '{name}' not found")
            return False
        return self._remove_player(player)
    
    def _confirm_and_remove_players(self, players_to_remove: List[Player], reason: str) -> int:
        """Helper to confirm and remove multiple players"""
        if not players_to_remove:
            return 0
        
        print(f"\n🗑️  Found {len(players_to_remove)} players {reason}:")
        for player in players_to_remove:
            print(f"  - {player.name} (ID: {player.player_id})")
        
        confirm = input(f"\n❓ Remove all {len(players_to_remove)} players? (y/N): ").strip().lower()
        if confirm != 'y':
            logger.info("Removal cancelled")
            return 0
        
        for player in players_to_remove:
            self._remove_player(player)
        
        logger.info(f"✅ Removed {len(players_to_remove)} players {reason}")
        return len(players_to_remove)
    
    def remove_players_by_position(self, position: str) -> int:
        """Remove all players with a specific position"""
        try:
            pos_enum = Position(position)
        except ValueError:
            logger.error(f"Invalid position: {position}")
            logger.info(f"Valid positions: {[p.value for p in Position]}")
            return 0
        
        players_to_remove = [p for p in self.registry.get_all_players() if pos_enum in p.positions]
        
        if not players_to_remove:
            logger.info(f"No players found with position {position}")
            return 0
        
        return self._confirm_and_remove_players(players_to_remove, f"with position {position}")
    
    def remove_players_by_stats_threshold(self, stat_name: str, threshold: float, 
                                        remove_below: bool = True) -> int:
        """Remove players based on stats threshold"""
        if stat_name not in ['level', 'stamina', 'speed']:
            logger.error(f"Invalid stat: {stat_name}. Valid stats: level, stamina, speed")
            return 0
        
        comparison = "below" if remove_below else "above"
        players_to_remove = [
            p for p in self.registry.get_all_players()
            if (remove_below and getattr(p.stats, stat_name) < threshold) or
               (not remove_below and getattr(p.stats, stat_name) > threshold)
        ]
        
        if not players_to_remove:
            logger.info(f"No players found with {stat_name} {comparison} {threshold}")
            return 0
        
        return self._confirm_and_remove_players(players_to_remove, f"with {stat_name} {comparison} {threshold}")
    
    def remove_inactive_players(self, player_ids: List[int]) -> int:
        """Remove specific players by ID list (for inactive players)"""
        if not player_ids:
            logger.error("No player IDs provided")
            return 0
        
        players_to_remove = []
        invalid_ids = []
        
        for player_id in player_ids:
            player = self.registry.get_player(player_id)
            if player:
                players_to_remove.append(player)
            else:
                invalid_ids.append(player_id)
        
        if invalid_ids:
            logger.warning(f"Invalid player IDs: {invalid_ids}")
        
        if not players_to_remove:
            logger.info("No valid players found to remove")
            return 0
        
        return self._confirm_and_remove_players(players_to_remove, "from inactive list")
    
    def interactive_removal(self) -> None:
        """Interactive player removal mode"""
        while True:
            print("\n" + "="*60)
            print("🎯 INTERACTIVE PLAYER REMOVAL")
            print("="*60)
            
            # Show current players
            self.list_players(show_stats=True)
            
            print("\nOptions:")
            print("1. Remove by ID")
            print("2. Remove by name")
            print("3. Remove by position")
            print("4. Remove by stats threshold")
            print("5. Remove multiple by IDs")
            print("0. Exit")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                try:
                    player_id = int(input("Enter player ID: "))
                    self.remove_player_by_id(player_id)
                except ValueError:
                    logger.error("Invalid ID")
            elif choice == '2':
                name = input("Enter player name: ").strip()
                if name:
                    self.remove_player_by_name(name)
            elif choice == '3':
                position = input("Enter position (DF, FW, CM, etc.): ").strip().upper()
                if position:
                    self.remove_players_by_position(position)
            elif choice == '4':
                stat = input("Enter stat (level/stamina/speed): ").strip().lower()
                if stat in ['level', 'stamina', 'speed']:
                    try:
                        threshold = float(input("Enter threshold: "))
                        comparison = input("Remove below threshold? (y/N): ").strip().lower()
                        remove_below = comparison == 'y'
                        self.remove_players_by_stats_threshold(stat, threshold, remove_below)
                    except ValueError:
                        logger.error("Invalid threshold")
            elif choice == '5':
                ids_input = input("Enter player IDs (comma-separated): ").strip()
                try:
                    player_ids = [int(id.strip()) for id in ids_input.split(',') if id.strip()]
                    self.remove_inactive_players(player_ids)
                except ValueError:
                    logger.error("Invalid ID format")
            else:
                logger.error("Invalid option")
    
    def backup_before_removal(self) -> Path:
        """Create backup before removal operations"""
        players = self.registry.get_all_players()
        backup_file = self.data_manager.backup_players(players)
        logger.info(f"📦 Backup created: {backup_file}")
        return backup_file
    
    def _save_changes(self) -> None:
        """Save changes to the registry"""
        players = self.registry.get_all_players()
        self.data_manager.save_players(players)
        logger.info(f"💾 Saved {len(players)} players to data file")

def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description="Player Management for Team Balancer")
    parser.add_argument('--list', action='store_true', help='List all players')
    parser.add_argument('--list-stats', action='store_true', help='List all players with stats')
    parser.add_argument('--remove-id', type=int, help='Remove player by ID')
    parser.add_argument('--remove-name', type=str, help='Remove player by name')
    parser.add_argument('--remove-position', type=str, help='Remove all players with position')
    parser.add_argument('--remove-stats', type=str, help='Remove players by stats (format: stat:threshold:below/above)')
    parser.add_argument('--remove-ids', type=str, help='Remove multiple players by IDs (comma-separated)')
    parser.add_argument('--interactive', action='store_true', help='Interactive removal mode')
    parser.add_argument('--backup', action='store_true', help='Create backup before operations')
    
    args = parser.parse_args()
    
    # Import time for backup timestamps
    import time
    
    manager = PlayerManager()
    
    # Create backup if requested
    if args.backup:
        manager.backup_before_removal()
    
    # Execute operations
    if args.list:
        manager.list_players()
    elif args.list_stats:
        manager.list_players(show_stats=True)
    elif args.remove_id:
        manager.remove_player_by_id(args.remove_id)
    elif args.remove_name:
        manager.remove_player_by_name(args.remove_name)
    elif args.remove_position:
        manager.remove_players_by_position(args.remove_position.upper())
    elif args.remove_stats:
        try:
            stat, threshold_str, comparison = args.remove_stats.split(':')
            threshold = float(threshold_str)
            remove_below = comparison.lower() == 'below'
            manager.remove_players_by_stats_threshold(stat, threshold, remove_below)
        except ValueError:
            logger.error("Invalid stats format. Use: stat:threshold:below/above")
            logger.info("Example: level:2.0:below")
    elif args.remove_ids:
        try:
            player_ids = [int(id.strip()) for id in args.remove_ids.split(',')]
            manager.remove_inactive_players(player_ids)
        except ValueError:
            logger.error("Invalid ID format. Use comma-separated IDs")
    elif args.interactive:
        manager.interactive_removal()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 