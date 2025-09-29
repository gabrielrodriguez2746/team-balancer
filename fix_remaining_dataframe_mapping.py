#!/usr/bin/env python3
"""
Fix remaining DataFrame to Player ID mapping issue in team_balancer_streamlit.py
"""

def fix_remaining_dataframe_mapping():
    """Fix the remaining DataFrame mapping issue in the separate page"""
    
    # Read the file
    with open('team_balancer_streamlit.py', 'r') as f:
        content = f.read()
    
    # Fix: In _show_separate_page - change multiselect to use player IDs
    old_separate_multiselect = '''        # Multi-select for separate players
        separate_indices = st.multiselect(
            "Select players who should NOT play together:",
            options=df.index,
            format_func=lambda x: f"{df.iloc[x]['Name']} (Level: {df.iloc[x]['Level']:.1f})"
        )
        
        # Update separate players
        st.session_state.separate_players = {df.iloc[i]['ID'] for i in separate_indices}'''
    
    new_separate_multiselect = '''        # Multi-select for separate players using player IDs as options
        separate_player_ids = st.multiselect(
            "Select players who should NOT play together:",
            options=df['ID'].tolist(),
            format_func=lambda x: f"{df[df['ID'] == x]['Name'].iloc[0]} (Level: {df[df['ID'] == x]['Level'].iloc[0]:.1f})"
        )
        
        # Update separate players
        st.session_state.separate_players = set(separate_player_ids)'''
    
    content = content.replace(old_separate_multiselect, new_separate_multiselect)
    
    # Write the file back
    with open('team_balancer_streamlit.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed remaining DataFrame to Player ID mapping issue")
    print("✅ Separate page multiselect now uses player IDs as options")

if __name__ == "__main__":
    fix_remaining_dataframe_mapping()
