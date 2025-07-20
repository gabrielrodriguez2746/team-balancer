#!/usr/bin/env python3

"""
Example usage of the team balancer with the new player model structure.
This demonstrates how to create players with custom stats and use the team balancer.
"""

from team_balancer import generate_balanced_teams, display_teams, POSITIONS_ALLOWED

def create_player_with_stats(player_id, name, positions, level, stamina=0, speed=0, nationality="🏳️"):
    """
    Helper function to create a player with the new Stats structure.
    
    Args:
        player_id (int): Unique player identifier
        name (str): Player name
        positions (list): List of positions the player can play
        level (float): Player's skill level (used for team balancing)
        stamina (int): Player's stamina stat (defaults to 0)
        speed (int): Player's speed stat (defaults to 0)
        nationality (str): Player's nationality flag
    
    Returns:
        dict: Player object with the new structure
    """
    return {
        "Id": player_id,
        "Name": name,
        "Position": positions,
        "Stats": {
            "level": level,
            "stamina": stamina,
            "speed": speed
        },
        "Nationality": nationality
    }

def main():
    """Example of creating custom players and generating balanced teams."""
    
    # Create some example players with custom stats
    custom_players = [
        create_player_with_stats(1, "Messi", ["FW", "RW"], 5.0, stamina=90, speed=85, nationality="🇦🇷"),
        create_player_with_stats(2, "Ronaldo", ["FW", "LW"], 4.9, stamina=88, speed=90, nationality="🇵🇹"),
        create_player_with_stats(3, "Neymar", ["FW", "LW"], 4.8, stamina=75, speed=88, nationality="🇧🇷"),
        create_player_with_stats(4, "Mbappé", ["FW", "RW"], 4.7, stamina=85, speed=95, nationality="🇫🇷"),
        create_player_with_stats(5, "Haaland", ["FW"], 4.6, stamina=80, speed=75, nationality="🇳🇴"),
        create_player_with_stats(6, "De Bruyne", ["MF", "CM"], 4.8, stamina=85, speed=70, nationality="🇧🇪"),
        create_player_with_stats(7, "Modric", ["MF", "CM"], 4.7, stamina=80, speed=65, nationality="🇭🇷"),
        create_player_with_stats(8, "Kimmich", ["DF", "MF"], 4.5, stamina=85, speed=75, nationality="🇩🇪"),
        create_player_with_stats(9, "Van Dijk", ["DF", "CB"], 4.6, stamina=85, speed=70, nationality="🇳🇱"),
        create_player_with_stats(10, "Alisson", ["GK"], 4.4, stamina=80, speed=60, nationality="🇧🇷"),
        create_player_with_stats(11, "Courtois", ["GK"], 4.3, stamina=85, speed=55, nationality="🇧🇪"),
        create_player_with_stats(12, "Dias", ["DF", "CB"], 4.4, stamina=80, speed=65, nationality="🇵🇹"),
    ]
    
    print("=== Example: Custom Players with Stats ===")
    print(f"Created {len(custom_players)} players with custom stats")
    print()
    
    # Show some example players
    print("Sample players:")
    for i, player in enumerate(custom_players[:3]):
        stats = player["Stats"]
        print(f"{i+1}. {player['Name']} ({', '.join(player['Position'])})")
        print(f"   Level: {stats['level']:.1f}, Stamina: {stats['stamina']}, Speed: {stats['speed']}")
        print(f"   Nationality: {player['Nationality']}")
        print()
    
    # Generate balanced teams
    print("=== Generating Balanced Teams ===")
    best_combinations = generate_balanced_teams(
        custom_players, 
        team_size=6, 
        must_be_separate=[], 
        must_be_same=[], 
        top_n=2
    )
    
    # Display the results
    display_teams(best_combinations)
    
    print("\n=== Example: Players with Different Stats ===")
    
    # Create players with varying stats to show the difference
    varied_players = [
        create_player_with_stats(1, "Fast Player", ["FW"], 3.0, stamina=60, speed=95, nationality="🇯🇲"),
        create_player_with_stats(2, "Strong Player", ["DF"], 4.0, stamina=95, speed=50, nationality="🇳🇴"),
        create_player_with_stats(3, "Balanced Player", ["MF"], 3.5, stamina=75, speed=75, nationality="🇩🇪"),
        create_player_with_stats(4, "Skilled Player", ["FW"], 4.5, stamina=70, speed=80, nationality="🇧🇷"),
        create_player_with_stats(5, "Endurance Player", ["MF"], 3.2, stamina=100, speed=60, nationality="🇰🇪"),
        create_player_with_stats(6, "Technical Player", ["FW"], 4.2, stamina=65, speed=70, nationality="🇪🇸"),
    ]
    
    print("Players with varied stats:")
    for player in varied_players:
        stats = player["Stats"]
        print(f"- {player['Name']}: Level {stats['level']:.1f}, Stamina {stats['stamina']}, Speed {stats['speed']}")
    
    print("\nGenerating teams...")
    varied_combinations = generate_balanced_teams(
        varied_players, 
        team_size=3, 
        must_be_separate=[], 
        must_be_same=[], 
        top_n=1
    )
    
    display_teams(varied_combinations)

if __name__ == "__main__":
    main() 