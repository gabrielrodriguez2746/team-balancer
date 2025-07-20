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

# Specify today's players by ID
players_today_ids = [11, 23, 20, 29, 37, 14, 33, 8, 18, 36, 38, 1]

# Filter positions and validate allowed positions
def filter_and_validate_positions(player, allowed_positions):
    valid_positions = [pos for pos in player["Position"] if pos in allowed_positions]
    if len(valid_positions) != len(player["Position"]):
        sys.exit(f"Error: Player '{player['Name']}' has an invalid position not in {allowed_positions}.")
    player["Position"] = valid_positions
    return player

# Verify the number of players
if len(players_today_ids) != TEAM_SIZE * 2:
    sys.exit(f"Error: 'players_today' should have {TEAM_SIZE * 2} players. Currently, it has {len(players_today_ids)}.")

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

        # Calculate average stats for balance (level, stamina, speed)
        team1_avg_level = sum(p["Stats"]["level"] for p in team1) / team_size
        team2_avg_level = sum(p["Stats"]["level"] for p in team2) / team_size
        level_diff = abs(team1_avg_level - team2_avg_level)
        
        team1_avg_stamina = sum(p["Stats"]["stamina"] for p in team1) / team_size
        team2_avg_stamina = sum(p["Stats"]["stamina"] for p in team2) / team_size
        stamina_diff = abs(team1_avg_stamina - team2_avg_stamina)
        
        team1_avg_speed = sum(p["Stats"]["speed"] for p in team1) / team_size
        team2_avg_speed = sum(p["Stats"]["speed"] for p in team2) / team_size
        speed_diff = abs(team1_avg_speed - team2_avg_speed)
        
        # Calculate total balance score (weighted sum of all stat differences)
        # You can adjust these weights to prioritize certain stats
        total_balance_score = level_diff + stamina_diff + speed_diff

        # Add this combination to the best_combinations list
        best_combinations.append((team1, team2, team1_avg_level, team2_avg_level, total_balance_score, 
                                 team1_avg_stamina, team2_avg_stamina, team1_avg_speed, team2_avg_speed))

    print(f"Total valid combinations before diversity filter: {len(best_combinations)}")

    # Apply diversity filter
    diverse_combinations = []
    for team1, team2, team1_avg, team2_avg, total_score, team1_stamina, team2_stamina, team1_speed, team2_speed in best_combinations:
        if all(
            len(set(player['Id'] for player in team1) & set(player['Id'] for player in existing_team1)) <= diversity_threshold
            and len(set(player['Id'] for player in team2) & set(player['Id'] for player in existing_team2)) <= diversity_threshold
            for existing_team1, existing_team2, _, _, _, _, _, _, _ in diverse_combinations
        ):
            diverse_combinations.append((team1, team2, team1_avg, team2_avg, total_score, 
                                       team1_stamina, team2_stamina, team1_speed, team2_speed))

    print(f"Total valid combinations after diversity filter: {len(diverse_combinations)}")

    # Select the top N combinations after diversity filtering
    diverse_combinations = sorted(diverse_combinations, key=lambda x: x[4])[:top_n]  # Sort by total_score (index 4)

    return diverse_combinations

# Display teams
def display_teams(best_combinations):
    for idx, (team1, team2, team1_avg, team2_avg, total_score, team1_stamina, team2_stamina, team1_speed, team2_speed) in enumerate(best_combinations, 1):
        print(f"\n**Opción {idx} - Puntuación de Balance Total: {total_score:.2f}**")
        print(f"**Diferencias:** Nivel: {abs(team1_avg - team2_avg):.2f}, Stamina: {abs(team1_stamina - team2_stamina):.2f}, Velocidad: {abs(team1_speed - team2_speed):.2f}")
        
        print(f"\n**Equipo 1 - Promedios:** Nivel: {team1_avg:.2f}, Stamina: {team1_stamina:.2f}, Velocidad: {team1_speed:.2f}")
        for i, player in enumerate(team1, 1):
            stats = player['Stats']
            print(f"{i}. {player['Name']} ({', '.join(player['Position'])}) - Nivel: {stats['level']:.1f}, Stamina: {stats['stamina']:.1f}, Velocidad: {stats['speed']:.1f}")

        print(f"\n**Equipo 2 - Promedios:** Nivel: {team2_avg:.2f}, Stamina: {team2_stamina:.2f}, Velocidad: {team2_speed:.2f}")
        for i, player in enumerate(team2, 1):
            stats = player['Stats']
            print(f"{i}. {player['Name']} ({', '.join(player['Position'])}) - Nivel: {stats['level']:.1f}, Stamina: {stats['stamina']:.1f}, Velocidad: {stats['speed']:.1f}")

# Run the program
def main():
    best_combinations = generate_balanced_teams(players_today)
    display_teams(best_combinations)

if __name__ == "__main__":
    main()
