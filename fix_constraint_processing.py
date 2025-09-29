#!/usr/bin/env python3
"""
Fix constraint processing logic in team_balancer_streamlit.py
"""

def fix_constraint_processing():
    """Fix the constraint processing logic"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic constraint processing section
    old_constraint_processing = '''            # Filter out invalid player IDs that are not in selected players
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))
            # Per-team together constraints (players who should be on specific teams)
            if st.session_state.get("per_team_together_constraints"):
                for team_num, player_ids in st.session_state.per_team_together_constraints.items():
                    # Filter out invalid player IDs
                    valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]
                    if valid_player_ids and len(valid_player_ids) != len(player_ids):
                        print(f"   Warning: Filtered out invalid player IDs for team {team_num}: {set(player_ids) - set(valid_player_ids)}")
                    player_ids = valid_player_ids
                    # Filter out invalid player IDs
                    valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]
                    if valid_player_ids and len(valid_player_ids) != len(player_ids):
                        print(f"   Warning: Filtered out invalid player IDs for team {team_num}: {set(player_ids) - set(valid_player_ids)}")
                    player_ids = valid_player_ids
                if player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [player_ids]
            
            # Filter out invalid player IDs that are not in selected players
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))
            # Basic validation: filter out invalid player IDs
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))'''
    
    new_constraint_processing = '''            # Filter out invalid player IDs that are not in selected players
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))
            
            # Per-team together constraints (players who should be on specific teams)
            if st.session_state.get("per_team_together_constraints"):
                for team_num, player_ids in st.session_state.per_team_together_constraints.items():
                    # Filter out invalid player IDs
                    valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]
                    if valid_player_ids and len(valid_player_ids) != len(player_ids):
                        print(f"   Warning: Filtered out invalid player IDs for team {team_num}: {set(player_ids) - set(valid_player_ids)}")
                    if valid_player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [valid_player_ids]'''
    
    content = content.replace(old_constraint_processing, new_constraint_processing)
    
    # Write the file back
    with open('team_balancer_streamlit.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed constraint processing logic")
    print("✅ Removed duplicate code and fixed indentation")
    print("✅ Fixed variable scope issues")

if __name__ == "__main__":
    fix_constraint_processing()
