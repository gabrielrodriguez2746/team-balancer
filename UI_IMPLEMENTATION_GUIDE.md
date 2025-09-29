# UI Implementation Guide - Preventing Reversion

## 🚨 CRITICAL: Per-Team Constraint Implementation

The `_show_together_page` method MUST use the per-team constraint interface, NOT the old single-group interface.

### ✅ CORRECT Implementation

```python
def _show_together_page(self):
    """Show the per-team 'players should play together' page"""
    # ... header and validation ...
    
    # Initialize per-team constraints if not exists
    if 'per_team_together_constraints' not in st.session_state:
        st.session_state.per_team_together_constraints = {}
    
    # Get number of teams
    num_teams = st.session_state.get('num_teams', 2)
    
    # Create tabs for each team
    team_tabs = st.tabs([f"Team {i+1}" for i in range(num_teams)])
    
    for team_number, tab in enumerate(team_tabs, 1):
        with tab:
            st.markdown(f"### Team {team_number} - Players Who Must Play Together")
            
            # Multi-select for this team
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
                del st.session_state.per_team_together_constraints[team_number]
```

### ❌ INCORRECT Implementation (DO NOT USE)

```python
def _show_together_page(self):
    """Show the 'players should play together' page"""
    # ... old single-group implementation ...
    
    # Multi-select for together players
    together_indices = st.multiselect(
        "Select players who should play together:",
        options=df.index,
        format_func=lambda x: f"{df.iloc[x]['Name']} (Level: {df.iloc[x]['Level']:.1f})"
    )
    
    # Update together players
    st.session_state.together_players = {df.iloc[i]['ID'] for i in together_indices}
```

## 🔧 Constraint Processing

The constraint processing MUST include per-team constraints:

```python
# Prepare per-team constraints
per_team_together_constraints = {}

# Per-team together constraints (players who should be on specific teams)
if st.session_state.get("per_team_together_constraints"):
    for team_num, player_ids in st.session_state.per_team_together_constraints.items():
        if player_ids:  # Only add non-empty constraints
            per_team_together_constraints[team_num] = [player_ids]

# Log per-team constraints for debugging
print(f"   Per-team together constraints: {per_team_together_constraints}")
```

And in the TeamBalancerConfig:

```python
dynamic_config = TeamBalancerConfig(
    team_size=actual_team_size,
    num_teams=num_teams,
    top_n_teams=self.config.top_n_teams,
    diversity_threshold=self.config.diversity_threshold,
    must_be_on_different_teams=separate_constraints,
    must_be_on_same_teams=together_constraints,
    must_be_on_same_teams_by_team=per_team_together_constraints,  # ← CRITICAL!
    stat_weights=self.config.stat_weights
)
```

## 🧭 Navigation

Navigation MUST be correct:

- **Back button in together page**: `st.session_state.current_page = "create_teams"`
- **Continue button in together page**: `st.session_state.current_page = "separate"`
- **Back button in separate page**: `st.session_state.current_page = "create_teams"` (NOT "together")

## 🔍 Verification Commands

Run these commands to verify the implementation:

```bash
# Check UI implementation
python prevent_ui_reversion.py

# Run comprehensive tests
python test_navigation_and_constraints.py

# Check syntax
python3 -m py_compile team_balancer_streamlit.py
```

## 🚨 What to Do If UI Reverts

1. **DO NOT** use `git checkout` on `team_balancer_streamlit.py` without checking
2. **ALWAYS** run `python prevent_ui_reversion.py` after any changes
3. **REPLACE** the `_show_together_page` method with the correct implementation
4. **VERIFY** constraint processing includes `per_team_together_constraints`
5. **TEST** with `python test_navigation_and_constraints.py`

## 📋 Key Elements to Check

- ✅ `per_team_together_constraints` in session state
- ✅ `team_tabs = st.tabs([f"Team {i+1}" for i in range(num_teams)])`
- ✅ `must_be_on_same_teams_by_team=per_team_together_constraints`
- ✅ Correct navigation flow
- ✅ Unique keys for multiselect widgets
- ✅ Proper constraint processing logic

## 🎯 Success Criteria

The application is working correctly when:
- ✅ Per-team constraint tabs are visible
- ✅ Players can be assigned to specific teams
- ✅ Constraints are respected in team generation
- ✅ Navigation flows correctly between pages
- ✅ All tests pass
