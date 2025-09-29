#!/usr/bin/env python3
"""
Debug test to understand why constraints are failing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig
from data_manager import DataManager, AppConfig
from player_manager import PlayerRegistry

def test_constraint_debug():
    """Test why constraints are failing"""
    
    print("🧪 Testing constraint debug...")
    
    # Load players
    config = AppConfig()
    data_manager = DataManager(config)
    players = data_manager.load_players()
    
    print(f"📊 Loaded {len(players)} players")
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Create a simple test case
    selected_player_ids = [1, 3, 5, 6, 8, 9, 12, 13, 18, 19, 21, 22, 24, 25, 27, 30, 31, 34, 35, 36, 37, 38, 39, 40]
    print(f"🎯 Selected player IDs: {selected_player_ids}")
    
    # Test constraint: Team 1 should have players [30, 27, 24, 22, 18]
    per_team_constraints = {1: [[30, 27, 24, 22, 18]]}
    print(f"🔗 Per-team constraints: {per_team_constraints}")
    
    # Create config
    config = TeamBalancerConfig(
        team_size=6,
        num_teams=4,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team=per_team_constraints,
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    # Create balancer
    balancer = TeamBalancer(config, registry)
    
    # Test a simple team combination
    # Let's create a team that SHOULD satisfy the constraint
    team1_players = []
    team2_players = []
    team3_players = []
    team4_players = []
    
    # Find players by ID
    player_map = {p.player_id: p for p in players}
    
    # Team 1: Should have [30, 27, 24, 22, 18] + 1 more
    constraint_players = [30, 27, 24, 22, 18]
    for pid in constraint_players:
        if pid in player_map:
            team1_players.append(player_map[pid])
    
    # Add one more player to team 1
    for pid in selected_player_ids:
        if pid not in constraint_players and pid in player_map:
            team1_players.append(player_map[pid])
            break
    
    # Fill other teams with remaining players
    remaining_players = []
    for pid in selected_player_ids:
        if pid in player_map and pid not in [p.player_id for p in team1_players]:
            remaining_players.append(player_map[pid])
    
    # Distribute remaining players
    for i, player in enumerate(remaining_players):
        if i < 6:
            team2_players.append(player)
        elif i < 12:
            team3_players.append(player)
        else:
            team4_players.append(player)
    
    # Create teams
    teams = [team1_players, team2_players, team3_players, team4_players]
    
    print(f"🏆 Team 1 players: {[p.player_id for p in team1_players]}")
    print(f"🏆 Team 2 players: {[p.player_id for p in team2_players]}")
    print(f"🏆 Team 3 players: {[p.player_id for p in team3_players]}")
    print(f"🏆 Team 4 players: {[p.player_id for p in team4_players]}")
    
    # Test constraint checking
    print(f"🔍 Testing constraint check...")
    result = balancer._check_constraints(teams)
    print(f"✅ Constraint check result: {result}")
    
    # Let's also test if the constraint players are actually in the selected players
    print(f"🔍 Constraint players [30, 27, 24, 22, 18] in selected players: {all(pid in selected_player_ids for pid in [30, 27, 24, 22, 18])}")
    
    # Check if players exist
    for pid in [30, 27, 24, 22, 18]:
        if pid in player_map:
            print(f"✅ Player {pid} exists: {player_map[pid].name}")
        else:
            print(f"❌ Player {pid} does not exist!")
    
    # Let's test the constraint logic step by step
    print(f"\n🔍 Step-by-step constraint analysis:")
    team_ids_sets = [{p.player_id for p in team} for team in teams]
    print(f"Team IDs sets: {team_ids_sets}")
    
    # Check per-team constraints
    for team_index_1_based, groups in per_team_constraints.items():
        print(f"Checking team {team_index_1_based} constraints: {groups}")
        if not (1 <= team_index_1_based <= len(team_ids_sets)):
            print(f"❌ Team index {team_index_1_based} is out of range!")
            continue
        
        team_ids = team_ids_sets[team_index_1_based - 1]
        print(f"Team {team_index_1_based} IDs: {team_ids}")
        
        for group in groups:
            print(f"Checking group {group}")
            if not all(pid in team_ids for pid in group):
                print(f"❌ Group {group} not all in team {team_index_1_based}")
                missing = [pid for pid in group if pid not in team_ids]
                print(f"Missing players: {missing}")
            else:
                print(f"✅ Group {group} all in team {team_index_1_based}")

if __name__ == "__main__":
    test_constraint_debug()
