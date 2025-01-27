#!/usr/bin/env python3

from itertools import combinations
import sys

# Configuration - Editable settings
TEAM_SIZE = 6
TOP_N_TEAMS = 3
MUST_BE_ON_DIFFERENT_TEAMS = [[15, 23]]  # Use player IDs 
MUST_BE_ON_SAME_TEAMS = [[]] # Use player IDs 
POSITIONS_ALLOWED = ["GK", "DF", "MF", "FW", "LW", "RW", "CM", "CB", "LB", "RB"]

# Full list of available players with unique IDs
all_players = [
    {"Id": 1, "Name": "Cesar", "Position": ["DF"], "Rating": 3.5, "Nationality": "🇨🇱"},
    {"Id": 2, "Name": "Lucas FC", "Position": ["FW"], "Rating": 3.8, "Nationality": "🇦🇷"},
    {"Id": 3, "Name": "Nico Laderach", "Position": ["DF"], "Rating": 3.6, "Nationality": "🇦🇷"},
    {"Id": 4, "Name": "Tomazzo", "Position": ["LW"], "Rating": 2.1, "Nationality": "🇧🇷"},
    {"Id": 5, "Name": "Alexsandro", "Position": ["CM"], "Rating": 3.3, "Nationality": "🇧🇷"},
    {"Id": 6, "Name": "Edu", "Position": ["DF"], "Rating": 1.0, "Nationality": "🇪🇸🇪🇨"},
    {"Id": 7, "Name": "Sergio Borne", "Position": ["RW"], "Rating": 3.2, "Nationality": "🇪🇸"},
    {"Id": 8, "Name": "Ale Masferrer", "Position": ["FW"], "Rating": 3.5, "Nationality": "🇪🇸"},
    {"Id": 9, "Name": "Pablo", "Position": ["RW"], "Rating": 4.0, "Nationality": "🇲🇽"},
    {"Id": 10, "Name": "Davide", "Position": ["FW", "CM"], "Rating": 4.0, "Nationality": "🇮🇹"},
    {"Id": 11, "Name": "Gabo", "Position": ["CM"], "Rating": 4.0, "Nationality": "🇻🇪"},
    {"Id": 12, "Name": "Shapi", "Position": ["RW"], "Rating": 2.3, "Nationality": "🇻🇪"},
    {"Id": 13, "Name": "Leo", "Position": ["LW"], "Rating": 3.55, "Nationality": "🇦🇷"},
    {"Id": 14, "Name": "Roger", "Position": ["DF"], "Rating": 3.7, "Nationality": "🇪🇸"},
    {"Id": 15, "Name": "Fran", "Position": ["LW"], "Rating": 2.5, "Nationality": "🇪🇸"},
    {"Id": 16, "Name": "Isra", "Position": ["RW"], "Rating": 2.2, "Nationality": "🇻🇪"},
    {"Id": 17, "Name": "Luis", "Position": ["CM"], "Rating": 3.7, "Nationality": "🇪🇸"},
    {"Id": 18, "Name": "Emmanuel", "Position": ["FW"], "Rating": 1.2, "Nationality": "🇬🇧"},
    {"Id": 19, "Name": "Salta", "Position": ["FW", "CM"], "Rating": 4.0, "Nationality": "🇦🇷"},
    {"Id": 20, "Name": "Juan Salamone", "Position": ["RW"], "Rating": 3.5, "Nationality": "🇦🇷"},
    {"Id": 21, "Name": "Victor Victor Victor", "Position": ["DF"], "Rating": 3.3, "Nationality": "🇨🇴"},
    {"Id": 22, "Name": "Amirhossein", "Position": ["FW"], "Rating": 2.8, "Nationality": "🇮🇷"},
    {"Id": 23, "Name": "Victor Lopez", "Position": ["DF"], "Rating": 2.4, "Nationality": "🇨🇴"},
    {"Id": 24, "Name": "Jose", "Position": ["RW"], "Rating": 3.8, "Nationality": "🇻🇪"},
    {"Id": 25, "Name": "Diego", "Position": ["DF"], "Rating": 4.0, "Nationality": "🇨🇷"},
    {"Id": 26, "Name": "Sergio Pino", "Position": ["RW"], "Rating": 2.8, "Nationality": "🇪🇸"},
    {"Id": 27, "Name": "Peluk", "Position": ["CM"], "Rating": 4.0, "Nationality": "🇪🇸"},
    {"Id": 28, "Name": "Checo", "Position": ["DF"], "Rating": 4.0, "Nationality": "🇲🇽"},
]

# Specify today's players by ID
players_today_ids = [2, 11, 27, 28, 15, 20, 16, 22, 14, 23, 18, 3]

# Verify the number of players
if len(players_today_ids) != TEAM_SIZE * 2:
    sys.exit(f"Error: 'players_today' should have {TEAM_SIZE * 2} players. Currently, it has {len(players_today_ids)}.")

# Filter positions and validate allowed positions
def filter_and_validate_positions(player, allowed_positions):
    valid_positions = [pos for pos in player["Position"] if pos in allowed_positions]
    if len(valid_positions) != len(player["Position"]):
        sys.exit(f"Error: Player '{player['Name']}' has an invalid position not in {allowed_positions}.")
    player["Position"] = valid_positions
    return player

# Map players_today_ids to player data, filtering and validating positions
players_today = [filter_and_validate_positions(player, POSITIONS_ALLOWED) for player in all_players if player["Id"] in players_today_ids]

# Function to generate balanced teams
def generate_balanced_teams(players, team_size=TEAM_SIZE, must_be_separate=MUST_BE_ON_DIFFERENT_TEAMS, 
                            must_be_same=MUST_BE_ON_SAME_TEAMS, top_n=TOP_N_TEAMS, diversity_threshold=TEAM_SIZE/2):
    best_combinations = []
    unique_combinations = set()  # To store unique team configurations
    
    # Filter active constraints for players present today
    active_must_be_same = [group for group in must_be_same if len([p for p in group if any(p == pl["Id"] for pl in players)]) > 1]
    active_must_be_separate = [group for group in must_be_separate if len([p for p in group if any(p == pl["Id"] for pl in players)]) > 1]
    
    for combination in combinations(players, team_size):
        team1 = list(combination)
        team2 = [p for p in players if p not in team1]
        
        # Ensure specified players are in separate teams
        team1_ids = {p['Id'] for p in team1}
        team2_ids = {p['Id'] for p in team2}
        if any(all(pid in team1_ids for pid in group) or all(pid in team2_ids for pid in group) for group in active_must_be_separate):
            continue  # Skip this combination if a group of must-be-separate players are in the same team
        
        # Ensure specified players are in the same team
        same_team_violation = False
        for group in active_must_be_same:
            in_team1 = all(pid in team1_ids for pid in group)
            in_team2 = all(pid in team2_ids for pid in group)
            if not (in_team1 or in_team2):  # If they're not all in the same team
                same_team_violation = True
                break
        
        if same_team_violation:
            continue  # Skip this combination if must-be-same players are not in the same team
        
        # Sort player IDs in each team to ensure unique identification
        sorted_team1 = tuple(sorted(player["Id"] for player in team1))
        sorted_team2 = tuple(sorted(player["Id"] for player in team2))
        combination_key = (sorted_team1, sorted_team2) if sorted_team1 < sorted_team2 else (sorted_team2, sorted_team1)
        
        # Check if this team configuration is unique
        if combination_key in unique_combinations:
            continue  # Skip if we've already seen this configuration
        
        # Add unique team configuration to the set
        unique_combinations.add(combination_key)
        
        # Calculate average ratings for balance
        team1_avg_rating = sum(p["Rating"] for p in team1) / team_size
        team2_avg_rating = sum(p["Rating"] for p in team2) / team_size
        rating_diff = abs(team1_avg_rating - team2_avg_rating)
        
        # Add this combination to the best_combinations list
        best_combinations.append((team1, team2, team1_avg_rating, team2_avg_rating, rating_diff))
    
    print(f"Total valid combinations before diversity filter: {len(best_combinations)}")
    
    # Apply diversity filter
    diverse_combinations = []
    for team1, team2, team1_avg, team2_avg, diff in best_combinations:
        if all(
            len(set(player['Id'] for player in team1) & set(player['Id'] for player in existing_team1)) <= diversity_threshold
            and len(set(player['Id'] for player in team2) & set(player['Id'] for player in existing_team2)) <= diversity_threshold
            for existing_team1, existing_team2, _, _, _ in diverse_combinations
        ):
            diverse_combinations.append((team1, team2, team1_avg, team2_avg, diff))
    
    print(f"Total valid combinations after diversity filter: {len(diverse_combinations)}")
    
    # Select the top N combinations after diversity filtering
    diverse_combinations = sorted(diverse_combinations, key=lambda x: x[-1])[:top_n]
    
    return diverse_combinations

# Display teams
def display_teams(best_combinations):
    for idx, (team1, team2, team1_avg, team2_avg, diff) in enumerate(best_combinations, 1):
        print(f"\n**Opción {idx} - Diferencia de Puntaje: {diff:.2f}**")
        print("\n**Equipo 1 (Puntuación promedio: {:.2f}):**".format(team1_avg))
        for i, player in enumerate(team1, 1):
            print(f"{i}. {player['Name']} ({', '.join(player['Position'])})")
        
        print("\n**Equipo 2 (Puntuación promedio: {:.2f}):**".format(team2_avg))
        for i, player in enumerate(team2, 1):
            print(f"{i}. {player['Name']} ({', '.join(player['Position'])})")

# Run the program
def main():
    best_combinations = generate_balanced_teams(players_today)
    display_teams(best_combinations)

if __name__ == "__main__":
    main()
