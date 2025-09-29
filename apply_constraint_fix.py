#!/usr/bin/env python3
"""
Apply constraint validation fix to team_balancer_streamlit.py
"""

def apply_constraint_fix():
    """Apply the constraint validation fix"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Find the constraint processing section and add validation
    old_section = '''            # Per-team together constraints (players who should be on specific teams)
            if st.session_state.get("per_team_together_constraints"):
                for team_num, player_ids in st.session_state.per_team_together_constraints.items():
                    if player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [player_ids]'''
    
    new_section = '''            # Per-team together constraints (players who should be on specific teams)
            # Filter out invalid player IDs that are not in selected players
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))
            
            if st.session_state.get("per_team_together_constraints"):
                for team_num, player_ids in st.session_state.per_team_together_constraints.items():
                    # Filter out invalid player IDs
                    valid_player_ids = [pid for pid in player_ids if pid in selected_player_ids]
                    if valid_player_ids and len(valid_player_ids) != len(player_ids):
                        print(f"   Warning: Filtered out invalid player IDs for team {team_num}: {set(player_ids) - set(valid_player_ids)}")
                    player_ids = valid_player_ids
                    if player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [player_ids]'''
    
    # Replace the section
    if old_section in content:
        content = content.replace(old_section, new_section)
        
        # Write the file back
        with open('team_balancer_streamlit.py', 'w') as f:
            f.write(content)
        
        print("✅ Applied constraint validation fix")
        return True
    else:
        print("❌ Could not find the constraint processing section")
        return False

if __name__ == "__main__":
    apply_constraint_fix()
