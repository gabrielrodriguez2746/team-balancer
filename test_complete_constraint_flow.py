#!/usr/bin/env python3
"""
Test to verify the complete constraint flow from UI to team generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig, PlayerRegistry, Player, PlayerStats, Position
from config import AppConfig

def test_complete_constraint_flow():
    """Test the complete constraint flow"""
    print("🧪 Testing Complete Constraint Flow...")
    
    # Create test players
    players = [
        Player("Player1", [Position.MF], PlayerStats(level=4.0, stamina=3.5, speed=3.5)),
        Player("Player2", [Position.DF], PlayerStats(level=3.5, stamina=3.0, speed=3.0)),
        Player("Player3", [Position.FW], PlayerStats(level=4.5, stamina=4.0, speed=4.0)),
        Player("Player4", [Position.MF], PlayerStats(level=3.0, stamina=2.5, speed=2.5)),
        Player("Player5", [Position.DF], PlayerStats(level=3.8, stamina=3.5, speed=3.5)),
        Player("Player6", [Position.FW], PlayerStats(level=4.2, stamina=3.8, speed=3.8)),
    ]
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Test per-team constraints
    print("\n🔗 Testing Per-Team Constraints...")
    
    # Constraint: Players 1,2 must be on Team 1; Players 3,4 must be on Team 2
    config = TeamBalancerConfig(
        team_size=3,
        num_teams=2,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team={
            1: [[1, 2]],  # Players 1,2 must be on Team 1
            2: [[3, 4]]   # Players 3,4 must be on Team 2
        },
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    balancer = TeamBalancer(config, registry)
    
    # Generate teams
    print("⚽ Generating teams with per-team constraints...")
    teams = balancer.generate_balanced_teams([1, 2, 3, 4, 5, 6])
    
    if not teams:
        print("❌ No teams generated!")
        return False
    
    print(f"✅ Generated {len(teams)} team combinations")
    
    # Check if constraints are respected
    for i, team_combination in enumerate(teams):
        print(f"\n🎯 Checking Team Combination #{i+1}:")
        
        # Check Team 1 constraints
        team1_players = [p.player_id for p in team_combination.teams[0]]
        team2_players = [p.player_id for p in team_combination.teams[1]]
        
        print(f"   Team 1 players: {team1_players}")
        print(f"   Team 2 players: {team2_players}")
        
        # Check if players 1,2 are on Team 1
        if 1 in team1_players and 2 in team1_players:
            print("   ✅ Players 1,2 are correctly on Team 1")
        else:
            print("   ❌ Players 1,2 are NOT on Team 1")
            return False
        
        # Check if players 3,4 are on Team 2
        if 3 in team2_players and 4 in team2_players:
            print("   ✅ Players 3,4 are correctly on Team 2")
        else:
            print("   ❌ Players 3,4 are NOT on Team 2")
            return False
    
    print("\n✅ All constraints are respected!")
    return True

def test_constraint_checking_method():
    """Test the _check_constraints method directly"""
    print("\n🔍 Testing _check_constraints method directly...")
    
    # Create test players
    players = [
        Player("Player1", [Position.MF], PlayerStats(level=4.0, stamina=3.5, speed=3.5)),
        Player("Player2", [Position.DF], PlayerStats(level=3.5, stamina=3.0, speed=3.0)),
        Player("Player3", [Position.FW], PlayerStats(level=4.5, stamina=4.0, speed=4.0)),
        Player("Player4", [Position.MF], PlayerStats(level=3.0, stamina=2.5, speed=2.5)),
    ]
    
    # Create player registry
    registry = PlayerRegistry()
    for player in players:
        registry.add_player(player)
    
    # Test configuration with per-team constraints
    config = TeamBalancerConfig(
        team_size=2,
        num_teams=2,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team={
            1: [[1, 2]],  # Players 1,2 must be on Team 1
            2: [[3, 4]]   # Players 3,4 must be on Team 2
        },
        stat_weights={"level": 1.0, "stamina": 1.0, "speed": 1.0}
    )
    
    balancer = TeamBalancer(config, registry)
    
    # Test valid combination
    valid_teams = [
        [players[0], players[1]],  # Team 1: Players 1,2
        [players[2], players[3]]   # Team 2: Players 3,4
    ]
    
    is_valid = balancer._check_constraints(valid_teams)
    print(f"   Valid combination check: {is_valid}")
    
    if not is_valid:
        print("   ❌ Valid combination failed constraint check!")
        return False
    
    # Test invalid combination
    invalid_teams = [
        [players[0], players[2]],  # Team 1: Players 1,3 (wrong!)
        [players[1], players[3]]  # Team 2: Players 2,4 (wrong!)
    ]
    
    is_invalid = balancer._check_constraints(invalid_teams)
    print(f"   Invalid combination check: {is_invalid}")
    
    if is_invalid:
        print("   ❌ Invalid combination passed constraint check!")
        return False
    
    print("   ✅ Constraint checking method works correctly!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Complete Constraint Flow Test")
    
    success1 = test_complete_constraint_flow()
    success2 = test_constraint_checking_method()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! Constraints are working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED! There are issues with the constraint system.")
        sys.exit(1)
