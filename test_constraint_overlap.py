#!/usr/bin/env python3
"""
Check for overlapping player IDs in constraints
"""

def check_constraint_overlap():
    """Check if constraints have overlapping player IDs"""
    
    print("🔍 Checking for overlapping player IDs in constraints...")
    
    # Original constraints from the logs
    constraints = {
        1: [1, 3, 6, 13],  # Team 1
        2: [18, 27, 30, 24, 22],  # Team 2  
        3: [40, 31],  # Team 3
        4: [39, 38, 37]  # Team 4
    }
    
    print("📊 Original constraints:")
    for team, players in constraints.items():
        print(f"   Team {team}: {players}")
    
    # Check for overlaps
    all_constrained_players = []
    for team, players in constraints.items():
        all_constrained_players.extend(players)
    
    print(f"\n📊 All constrained players: {sorted(all_constrained_players)}")
    print(f"📊 Total constrained players: {len(all_constrained_players)}")
    print(f"📊 Unique constrained players: {len(set(all_constrained_players))}")
    
    if len(all_constrained_players) != len(set(all_constrained_players)):
        print("❌ OVERLAP DETECTED!")
        print("🔍 Some players are assigned to multiple teams!")
        
        # Find overlaps
        from collections import Counter
        player_counts = Counter(all_constrained_players)
        overlaps = {player: count for player, count in player_counts.items() if count > 1}
        
        print(f"🔍 Overlapping players: {overlaps}")
        
        # Show which teams each overlapping player is assigned to
        for player in overlaps:
            teams = [team for team, players in constraints.items() if player in players]
            print(f"   Player {player} is assigned to teams: {teams}")
    else:
        print("✅ No overlaps detected")
    
    # Check if total constrained players exceed available spots
    total_spots = 4 * 6  # 4 teams * 6 players each
    print(f"\n📊 Total team spots: {total_spots}")
    print(f"📊 Constrained players: {len(set(all_constrained_players))}")
    print(f"📊 Remaining spots: {total_spots - len(set(all_constrained_players))}")
    
    if len(set(all_constrained_players)) > total_spots:
        print("❌ IMPOSSIBLE: More constrained players than available spots!")
    elif len(set(all_constrained_players)) == total_spots:
        print("⚠️  RISKY: All spots are constrained (no flexibility)")
    else:
        print("✅ FEASIBLE: Constraints should be possible")

if __name__ == "__main__":
    check_constraint_overlap()
