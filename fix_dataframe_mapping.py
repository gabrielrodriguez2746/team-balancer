#!/usr/bin/env python3
"""
Fix DataFrame to Player ID mapping issue in team_balancer_streamlit.py
"""

def fix_dataframe_mapping():
    """Fix the DataFrame mapping issue by using player IDs as options instead of DataFrame indices"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Fix 1: In _show_create_teams_page - change multiselect to use player IDs
    old_create_teams_multiselect = '''        # Multi-select
        selected_indices = st.multiselect(
            "Select players for teams:",
            options=df.index,
            format_func=lambda x: f"{df.iloc[x]['Name']} (Level: {df.iloc[x]['Level']:.1f}, Total: {df.iloc[x]['Total']:.1f})"
        )
        
        # Update selected players
        st.session_state.selected_players = {df.iloc[i]['ID'] for i in selected_indices}'''
    
    new_create_teams_multiselect = '''        # Multi-select using player IDs as options
        selected_player_ids = st.multiselect(
            "Select players for teams:",
            options=df['ID'].tolist(),
            format_func=lambda x: f"{df[df['ID'] == x]['Name'].iloc[0]} (Level: {df[df['ID'] == x]['Level'].iloc[0]:.1f}, Total: {df[df['ID'] == x]['Total'].iloc[0]:.1f})"
        )
        
        # Update selected players
        st.session_state.selected_players = set(selected_player_ids)'''
    
    content = content.replace(old_create_teams_multiselect, new_create_teams_multiselect)
    
    # Fix 2: In _show_together_page - change multiselect to use player IDs
    old_together_multiselect = '''                # Multi-select for this team
                together_indices = st.multiselect(
                    f"Select players who must be on Team {team_number}:",
                    options=df.index,
                    format_func=lambda x: f"{df.iloc[x]['Name']} (Level: {df.iloc[x]['Level']:.1f})",
                    key=f"team_{team_number}_together"
                )
                
                # Update constraints
                if together_indices:
                    st.session_state.per_team_together_constraints[team_number] = [df.iloc[i]['ID'] for i in together_indices]
                elif team_number in st.session_state.per_team_together_constraints:
                    del st.session_state.per_team_together_constraints[team_number]'''
    
    new_together_multiselect = '''                # Multi-select for this team using player IDs as options
                together_player_ids = st.multiselect(
                    f"Select players who must be on Team {team_number}:",
                    options=df['ID'].tolist(),
                    format_func=lambda x: f"{df[df['ID'] == x]['Name'].iloc[0]} (Level: {df[df['ID'] == x]['Level'].iloc[0]:.1f})",
                    key=f"team_{team_number}_together"
                )
                
                # Update constraints
                if together_player_ids:
                    st.session_state.per_team_together_constraints[team_number] = together_player_ids
                elif team_number in st.session_state.per_team_together_constraints:
                    del st.session_state.per_team_together_constraints[team_number]'''
    
    content = content.replace(old_together_multiselect, new_together_multiselect)
    
    # Write the file back
    with open('team_balancer_streamlit.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed DataFrame to Player ID mapping issue")
    print("✅ Multiselect now uses player IDs as options instead of DataFrame indices")

if __name__ == "__main__":
    fix_dataframe_mapping()
