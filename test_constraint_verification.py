#!/usr/bin/env python3
"""
Test to verify that per-team constraints are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team_balancer import TeamBalancer, TeamBalancerConfig, PlayerRegistry, Player, PlayerStats, Position
from config import AppConfig

def test_per_team_constraints():
    """Test that per-team constraints are respected"""
    print("🧪 Testing per-team constraints...")
    
    # Create test configuration with per-team constraints
    config = TeamBalancerConfig(
        team_size=3,
        num_teams=2,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team={
            1: [[1, 2]],  # Players 1 and 2 must be on Team 1
            2: [[3, 4]]   # Players 3 and 4 must be on Team 2
        },
        stat_weights={'level': 1.0}
    )
    
    # Create player registry
    player_registry = PlayerRegistry()
    
    # Add test players
    test_players = [
        Player(name="Player1", positions=[Position.FW], stats=PlayerStats(level=3.0, stamina=3.5, speed=3.5), player_id=1),
        Player(name="Player2", positions=[Position.MF], stats=PlayerStats(level=3.5, stamina=3.8, speed=3.8), player_id=2),
        Player(name="Player3", positions=[Position.DF], stats=PlayerStats(level=4.0, stamina=3.0, speed=3.0), player_id=3),
        Player(name="Player4", positions=[Position.GK], stats=PlayerStats(level=2.5, stamina=2.5, speed=2.5), player_id=4),
        Player(name="Player5", positions=[Position.FW], stats=PlayerStats(level=3.8, stamina=4.0, speed=4.0), player_id=5),
        Player(name="Player6", positions=[Position.MF], stats=PlayerStats(level=3.2, stamina=3.5, speed=3.5), player_id=6)
    ]
    
    for player in test_players:
        player_registry.add_player(player)
    
    # Create TeamBalancer
    balancer = TeamBalancer(config, player_registry)
    
    # Test constraint checking
    try:
        # Test valid team combination (respects constraints)
        valid_teams = [
            [test_players[0], test_players[1], test_players[4]],  # Team 1: Players 1,2,5
            [test_players[2], test_players[3], test_players[5]]     # Team 2: Players 3,4,6
        ]
        
        is_valid = balancer._check_constraints(valid_teams)
        print(f"✅ Valid team combination (respects constraints): {is_valid}")
        
        # Test invalid team combination (violates constraints)
        invalid_teams = [
            [test_players[0], test_players[2], test_players[4]],  # Team 1: Players 1,3,5 (Player 3 should be on Team 2)
            [test_players[1], test_players[3], test_players[5]]   # Team 2: Players 2,4,6 (Player 2 should be on Team 1)
        ]
        
        is_invalid = balancer._check_constraints(invalid_teams)
        print(f"✅ Invalid team combination (violates constraints): {is_invalid}")
        
        if is_valid and not is_invalid:
            print("🎉 Constraint checking is working correctly!")
            return True
        else:
            print("❌ Constraint checking is not working correctly!")
            return False
            
    except Exception as e:
        print(f"❌ Error during constraint testing: {e}")
        return False

def test_team_generation_with_constraints():
    """Test that team generation respects constraints"""
    print("\n🧪 Testing team generation with constraints...")
    
    # Create test configuration with per-team constraints
    config = TeamBalancerConfig(
        team_size=2,
        num_teams=2,
        top_n_teams=3,
        diversity_threshold=0.1,
        must_be_on_different_teams=[],
        must_be_on_same_teams=[],
        must_be_on_same_teams_by_team={
            1: [[1, 2]],  # Players 1 and 2 must be on Team 1
            2: [[3, 4]]   # Players 3 and 4 must be on Team 2
        },
        stat_weights={'level': 1.0}
    )
    
    # Create player registry
    player_registry = PlayerRegistry()
    
    # Add test players
    test_players = [
        Player(name="Player1", positions=[Position.FW], stats=PlayerStats(level=3.0, stamina=3.5, speed=3.5), player_id=1),
        Player(name="Player2", positions=[Position.MF], stats=PlayerStats(level=3.5, stamina=3.8, speed=3.8), player_id=2),
        Player(name="Player3", positions=[Position.DF], stats=PlayerStats(level=4.0, stamina=3.0, speed=3.0), player_id=3),
        Player(name="Player4", positions=[Position.GK], stats=PlayerStats(level=2.5, stamina=2.5, speed=2.5), player_id=4)
    ]
    
    for player in test_players:
        player_registry.add_player(player)
    
    # Create TeamBalancer
    balancer = TeamBalancer(config, player_registry)
    
    try:
        # Generate teams
        player_ids = [1, 2, 3, 4]
        combinations = balancer.generate_balanced_teams(player_ids)
        
        print(f"✅ Generated {len(combinations)} team combinations")
        
        if combinations:
            # Check if constraints are respected in the first combination
            first_combination = combinations[0]
            teams = first_combination.teams
            
            # Check Team 1 constraints
            team1_player_ids = [p.player_id for p in teams[0]]
            team1_constraint_satisfied = all(pid in team1_player_ids for pid in [1, 2])
            
            # Check Team 2 constraints  
            team2_player_ids = [p.player_id for p in teams[1]]
            team2_constraint_satisfied = all(pid in team2_player_ids for pid in [3, 4])
            
            print(f"✅ Team 1 constraint satisfied: {team1_constraint_satisfied}")
            print(f"✅ Team 2 constraint satisfied: {team2_constraint_satisfied}")
            
            if team1_constraint_satisfied and team2_constraint_satisfied:
                print("🎉 Team generation respects constraints!")
                return True
            else:
                print("❌ Team generation does not respect constraints!")
                return False
        else:
            print("❌ No team combinations generated!")
            return False
            
    except Exception as e:
        print(f"❌ Error during team generation testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Constraint Verification Tests")
    print("=" * 50)
    
    success1 = test_per_team_constraints()
    success2 = test_team_generation_with_constraints()
    
    if success1 and success2:
        print("\n🎉 All constraint tests passed! Constraints are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some constraint tests failed. Constraints need more work.")
        sys.exit(1)
