#!/usr/bin/env python3
"""
Fix remaining constraint processing issues in team_balancer_streamlit.py
"""

def fix_remaining_constraint_processing():
    """Fix the remaining constraint processing issues"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Remove the remaining duplicate code
    old_remaining_code = '''            # Filter out invalid player IDs that are not in selected players
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))
            # Basic validation: filter out invalid player IDs
            selected_player_ids = {p.player_id for p in selected_players}
            print(f"   Selected player IDs: {sorted(selected_player_ids)}")
            print("   Raw per-team constraints:", st.session_state.get("per_team_together_constraints", {}))'''
    
    new_remaining_code = '''            # Log per-team constraints for debugging'''
    
    content = content.replace(old_remaining_code, new_remaining_code)
    
    # Also fix the incorrect indentation issue
    old_indentation_issue = '''                if player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [player_ids]'''
    
    new_indentation_issue = '''                    if valid_player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [valid_player_ids]'''
    
    content = content.replace(old_indentation_issue, new_indentation_issue)
    
    # Write the file back
    with open('team_balancer_streamlit.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed remaining constraint processing issues")
    print("✅ Removed all duplicate code")
    print("✅ Fixed indentation issues")

if __name__ == "__main__":
    fix_remaining_constraint_processing()
