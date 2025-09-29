#!/usr/bin/env python3
"""
Fix constraint validation by adding selected_player_ids definition before it's used
"""

def fix_constraint_validation():
    """Apply the constraint validation fix with proper indentation"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        lines = f.readlines()
    
    # Find the constraint processing section
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for the per-team constraints section
        if "# Per-team together constraints (players who should be on specific teams)" in line:
            # Add the selected_player_ids definition before this line
            new_lines.append("            # Filter out invalid player IDs that are not in selected players\n")
            new_lines.append("            selected_player_ids = {p.player_id for p in selected_players}\n")
            new_lines.append("            print(f\"   Selected player IDs: {sorted(selected_player_ids)}\")\n")
            new_lines.append("            print(\"   Raw per-team constraints:\", st.session_state.get(\"per_team_together_constraints\", {}))\n")
            new_lines.append(line)
            i += 1
            
            # Look for the for loop and add filtering logic
            while i < len(lines):
                current_line = lines[i]
                new_lines.append(current_line)
                
                if "for team_num, player_ids in st.session_state.per_team_together_constraints.items():" in current_line:
                    # Add filtering logic after the for loop
                    new_lines.append("                    # Filter out invalid player IDs\n")
                    new_lines.append("                    valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]\n")
                    new_lines.append("                    if valid_player_ids and len(valid_player_ids) != len(player_ids):\n")
                    new_lines.append("                        print(f\"   Warning: Filtered out invalid player IDs for team {team_num}: {set(player_ids) - set(valid_player_ids)}\")\n")
                    new_lines.append("                    player_ids = valid_player_ids\n")
                
                i += 1
                # Break if we've processed the constraint section
                if "if player_ids:" in current_line and "per_team_together_constraints[team_num]" in current_line:
                    break
        else:
            new_lines.append(line)
            i += 1
    
    # Write the file back
    with open('team_balancer_streamlit.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Applied constraint validation fix with proper indentation")

if __name__ == "__main__":
    fix_constraint_validation()
