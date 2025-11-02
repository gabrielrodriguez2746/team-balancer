#!/usr/bin/env python3
"""
Modern Team Balancer UI using Streamlit
A web-based interface for managing players and generating balanced teams.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional, Tuple
import json
import os
from datetime import datetime
import numpy as np # Added for standard deviation calculation

# Import existing modules
from team_balancer import TeamBalancer, PlayerRegistry, Player, PlayerStats, Position, TeamBalancerConfig
from data_manager import DataManager
from config import AppConfig


class StreamlitTeamBalancerUI:
    """Modern team balancer user interface using Streamlit"""
    
    def __init__(self):
        """Initialize the Streamlit UI"""
        # Load configuration
        self.config = AppConfig.load()
        
        # Initialize components
        self.data_manager = DataManager(self.config)
        self.player_registry = PlayerRegistry()
        
        # Create TeamBalancerConfig from AppConfig
        team_config = TeamBalancerConfig(
            team_size=self.config.team_size,
            top_n_teams=self.config.top_n_teams,
            diversity_threshold=self.config.diversity_threshold,
            must_be_on_different_teams=self.config.must_be_on_different_teams,
            must_be_on_same_teams=self.config.must_be_on_same_teams,
            stat_weights=self.config.stat_weights
        )
        
        self.team_balancer = TeamBalancer(team_config, self.player_registry)
        
        # Load existing players
        self._load_players()
        
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        defaults = {
            'selected_players': set(),
            'together_players': set(),
            'separate_players': set(),
            'team_size': 6,
            'current_page': "main"
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _player_to_dict(self, player: Player, include_total: bool = False) -> Dict:
        """Convert player to dictionary for DataFrame"""
        data = {
            'ID': player.player_id,
            'Name': player.name,
            'Positions': ', '.join([pos.value for pos in player.positions]),
            'Level': player.stats.level,
            'Stamina': player.stats.stamina,
            'Speed': player.stats.speed
        }
        if include_total:
            data['Total Stats'] = player.stats.level + player.stats.stamina + player.stats.speed
        return data
    
    def _players_to_dataframe(self, players: List[Player], include_total: bool = False) -> pd.DataFrame:
        """Convert list of players to pandas DataFrame"""
        return pd.DataFrame([self._player_to_dict(p, include_total) for p in players])
    
    def _format_positions(self, player: Player) -> str:
        """Format player positions as comma-separated string"""
        return ', '.join([pos.value for pos in player.positions])
    
    def _load_players(self):
        """Load players from file"""
        try:
            players = self.data_manager.load_players()
            for player in players:
                self.player_registry.add_player(player)
        except Exception as e:
            st.error(f"Error loading players: {e}")
    
    def run(self):
        """Run the main application"""
        st.set_page_config(
            page_title="Team Balancer",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #c3e6cb;
        }
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #f5c6cb;
        }
        .soccer-field-container {
            background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 100%);
            border-radius: 1rem;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .team-label {
            font-weight: bold;
            text-align: center;
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .team-a-label {
            background-color: rgba(255, 0, 0, 0.1);
            color: #d32f2f;
            border: 2px solid #d32f2f;
        }
        .team-b-label {
            background-color: rgba(0, 0, 255, 0.1);
            color: #1976d2;
            border: 2px solid #1976d2;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Navigation
        self._show_navigation()
        
        # Main content based on current page
        if st.session_state.current_page == "main":
            self._show_main_page()
        elif st.session_state.current_page == "players":
            self._show_players_page()
        elif st.session_state.current_page == "create_teams":
            self._show_create_teams_page()
        elif st.session_state.current_page == "together":
            self._show_together_page()
        elif st.session_state.current_page == "separate":
            self._show_separate_page()
        elif st.session_state.current_page == "results":
            self._show_results_page()
    
    def _show_navigation(self):
        """Show navigation sidebar"""
        st.sidebar.markdown("## 🧭 Navigation")
        
        # Main menu
        if st.sidebar.button("🏠 Main Menu", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()
        
        # Players management
        if st.sidebar.button("👥 Players", use_container_width=True):
            st.session_state.current_page = "players"
            st.rerun()
        
        # Create teams
        if st.sidebar.button("⚽ Create Teams", use_container_width=True):
            st.session_state.current_page = "create_teams"
            st.rerun()
        
        # Current page indicator
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Current Page:** {st.session_state.current_page.replace('_', ' ').title()}")
        
        # Stats
        players = self.player_registry.get_all_players()
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📊 Stats")
        st.sidebar.metric("Total Players", len(players))
        if st.session_state.selected_players:
            st.sidebar.metric("Selected Players", len(st.session_state.selected_players))
    
    def _show_main_page(self):
        """Show the main menu page"""
        st.markdown('<h1 class="main-header">⚽ Team Balancer</h1>', unsafe_allow_html=True)
        
        # Welcome message
        st.markdown("""
        Welcome to the Team Balancer! This application helps you manage players and create balanced teams.
        
        **Features:**
        - 👥 **Player Management**: Add, edit, and manage player profiles
        - ⚽ **Team Creation**: Generate balanced teams based on player stats
        - 🎯 **Constraints**: Set players who must play together or separately
        - 📊 **Analytics**: View team balance statistics and visualizations
        """)
        
        # Quick actions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Quick Actions")
            if st.button("👥 Manage Players", use_container_width=True, key="manage_players"):
                st.session_state.current_page = "players"
                st.rerun()
            
            if st.button("⚽ Create Teams", use_container_width=True, key="create_teams_btn"):
                st.session_state.current_page = "create_teams"
                st.rerun()
        
        with col2:
            st.markdown("### 📈 Statistics")
            players = self.player_registry.get_all_players()
            
            if players:
                df = self._players_to_dataframe(players)
                
                # Average stats
                avg_level = df['Level'].mean()
                avg_stamina = df['Stamina'].mean()
                avg_speed = df['Speed'].mean()
                
                st.metric("Average Level", f"{avg_level:.1f}")
                st.metric("Average Stamina", f"{avg_stamina:.1f}")
                st.metric("Average Speed", f"{avg_speed:.1f}")
            else:
                st.info("No players found. Add some players to get started!")
        
        # Recent activity
        st.markdown("### 📋 Recent Activity")
        if players:
            recent_players = players[-5:]  # Last 5 players
            for player in recent_players:
                st.markdown(f"**{player.name}** - Level {player.stats.level} - {self._format_positions(player)}")
        else:
            st.info("No recent activity. Start by adding players!")
    
    def _show_players_page(self):
        """Show the players management page"""
        st.markdown('<h1 class="sub-header">👥 Player Management</h1>', unsafe_allow_html=True)
        
        # CRUD operations
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("➕ Add Player", use_container_width=True, key="add_player"):
                self._show_add_player_form()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_players"):
                self._load_players()
                st.success("Players refreshed successfully!")
                st.rerun()
        
        with col3:
            if st.button("📊 View Stats", use_container_width=True, key="view_stats"):
                self._show_player_stats()
        
        # Player list
        players = self.player_registry.get_all_players()
        
        if players:
            df = self._players_to_dataframe(players, include_total=True)
            
            # Display with selection
            st.markdown("### 📋 Player List")
            selected_indices = st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Positions": st.column_config.TextColumn("Positions", width="medium"),
                    "Level": st.column_config.NumberColumn("Level", format="%.1f", width="small"),
                    "Stamina": st.column_config.NumberColumn("Stamina", format="%.1f", width="small"),
                    "Speed": st.column_config.NumberColumn("Speed", format="%.1f", width="small"),
                    "Total Stats": st.column_config.NumberColumn("Total", format="%.1f", width="small")
                }
            )
            
            # Player actions
            st.markdown("### 🛠️ Player Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                # Edit player
                player_names = [p.name for p in players]
                if player_names:
                    selected_player_name = st.selectbox("Select player to edit:", player_names)
                    
                    if st.button("✏️ Edit Player", type="primary", key="edit_player"):
                        selected_player = next(p for p in players if p.name == selected_player_name)
                        st.session_state.editing_player = selected_player
                        st.rerun()
                else:
                    st.info("No players available to edit.")
            
            with col2:
                # Delete player
                if player_names:
                    delete_player_name = st.selectbox("Select player to delete:", player_names)
                    
                    if st.button("🗑️ Delete Player", type="secondary", key="delete_player"):
                        if st.checkbox("Confirm deletion"):
                            self._delete_player(delete_player_name)
                            st.success(f"Player '{delete_player_name}' deleted successfully!")
                            st.rerun()
                else:
                    st.info("No players available to delete.")
            
            # Show edit form if a player is being edited
            if hasattr(st.session_state, 'editing_player') and st.session_state.editing_player:
                st.markdown("---")
                st.markdown("### ✏️ Editing Player")
                
                # Add a cancel button outside the form
                if st.button("❌ Cancel Edit", type="secondary", key="cancel_edit"):
                    del st.session_state.editing_player
                    st.rerun()
                
                # Show the edit form
                self._show_edit_player_form(st.session_state.editing_player)
        else:
            st.info("No players found. Add some players to get started!")
    
    def _show_add_player_form(self):
        """Show the add player form"""
        st.markdown("### ➕ Add New Player")
        
        with st.form("add_player_form"):
            name = st.text_input("Player Name", placeholder="Enter player name")
            
            # Positions
            positions = st.multiselect(
                "Positions",
                options=[pos.value for pos in Position],
                default=[]
            )
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                level = st.slider("Level", 1.0, 5.0, 3.0, 0.1)
            with col2:
                stamina = st.slider("Stamina", 1.0, 5.0, 3.0, 0.1)
            with col3:
                speed = st.slider("Speed", 1.0, 5.0, 3.0, 0.1)
            
            submitted = st.form_submit_button("Add Player")
            
            if submitted:
                if name and positions:
                    try:
                        # Create player
                        player = Player(
                            name=name,
                            positions=[Position(pos) for pos in positions],
                            stats=PlayerStats(level=level, stamina=stamina, speed=speed)
                        )
                        
                        # Add to registry
                        self.player_registry.add_player(player)
                        
                        # Save to file
                        players = self.player_registry.get_all_players()
                        self.data_manager.save_players(players)
                        
                        st.success(f"Player '{name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding player: {e}")
                else:
                    st.error("Please fill in all required fields.")
    
    def _show_edit_player_form(self, player: Player):
        """Show the edit player form"""
        st.markdown(f"### ✏️ Edit Player: {player.name}")
        
        # Store original values for comparison
        original_name = player.name
        original_positions = [pos.value for pos in player.positions]
        original_level = player.stats.level
        original_stamina = player.stats.stamina
        original_speed = player.stats.speed
        
        with st.form("edit_player_form"):
            name = st.text_input("Player Name", value=original_name)
            
            # Positions
            positions = st.multiselect(
                "Positions",
                options=[pos.value for pos in Position],
                default=original_positions
            )
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                level = st.slider("Level", 1.0, 5.0, original_level, 0.1)
            with col2:
                stamina = st.slider("Stamina", 1.0, 5.0, original_stamina, 0.1)
            with col3:
                speed = st.slider("Speed", 1.0, 5.0, original_speed, 0.1)
            
            submitted = st.form_submit_button("Update Player")
            
            if submitted:
                if name and positions:
                    try:
                        # Create new PlayerStats object
                        new_stats = PlayerStats(level=level, stamina=stamina, speed=speed)
                        
                        # Create updated player object
                        updated_player = Player(
                            name=name,
                            positions=[Position(pos) for pos in positions],
                            stats=new_stats,
                            player_id=player.player_id
                        )
                        
                        # Update player in registry
                        success = self.player_registry.update_player(player.player_id, updated_player)
                        if not success:
                            raise ValueError(f"Failed to update player with ID {player.player_id}")
                        
                        # Save to file
                        players = self.player_registry.get_all_players()
                        self.data_manager.save_players(players)
                        
                        # Show updated information
                        st.info(f"""
                        **Updated Player Information:**
                        - **Name**: {name}
                        - **Positions**: {', '.join(positions)}
                        - **Level**: {level:.1f}
                        - **Stamina**: {stamina:.1f}
                        - **Speed**: {speed:.1f}
                        - **Total Stats**: {level + stamina + speed:.1f}
                        """)
                        
                        # Clear the editing state to go back to players list
                        if 'editing_player' in st.session_state:
                            del st.session_state.editing_player
                        
                        # Force refresh of players list
                        st.success(f"Player '{name}' updated successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error updating player: {e}")
                        st.error(f"Details: {str(e)}")
                else:
                    st.error("Please fill in all required fields.")
                    if not name:
                        st.error("Player name is required.")
                    if not positions:
                        st.error("At least one position is required.")
    
    def _delete_player(self, player_name: str):
        """Delete a player"""
        try:
            # Find and remove player
            players = self.player_registry.get_all_players()
            player_to_delete = next(p for p in players if p.name == player_name)
            
            # Remove from registry
            self.player_registry.remove_player(player_to_delete.player_id)
            
            # Save to file
            players = self.player_registry.get_all_players()
            self.data_manager.save_players(players)
            
            st.success(f"Player '{player_name}' deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting player: {e}")
    
    def _show_player_stats(self):
        """Show player statistics"""
        players = self.player_registry.get_all_players()
        
        if not players:
            st.info("No players to display statistics for.")
            return
        
        # Convert to DataFrame
        stats_data = []
        for player in players:
            stats_data.append({
                'Name': player.name,
                'Level': player.stats.level,
                'Stamina': player.stats.stamina,
                'Speed': player.stats.speed,
                'Total': player.stats.level + player.stats.stamina + player.stats.speed
            })
        
        df = pd.DataFrame(stats_data)
        
        # Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Player Statistics")
            st.dataframe(df.describe(), use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Top Players")
            top_players = df.nlargest(5, 'Total')
            st.dataframe(top_players, use_container_width=True)
        
        # Charts
        st.markdown("### 📈 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Stats distribution
            fig = px.histogram(df, x=['Level', 'Stamina', 'Speed'], 
                             title="Stats Distribution",
                             barmode='overlay')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Scatter plot
            fig = px.scatter(df, x='Level', y='Stamina', 
                           size='Speed', hover_data=['Name'],
                           title="Level vs Stamina (Size = Speed)")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_create_teams_page(self):
        """Show the team creation page"""
        st.markdown('<h1 class="sub-header">⚽ Create Teams</h1>', unsafe_allow_html=True)
        
        players = self.player_registry.get_all_players()
        
        if not players:
            st.error("No players available. Please add some players first.")
            return
        
        # Team configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚙️ Team Configuration")
            
            # Number of teams selector
            selected_count = len(st.session_state.selected_players)
            if selected_count >= 4:
                max_possible_teams = min(6, selected_count // 2)  # Max 6 teams, min 2 players per team
                min_teams = 2
                
                if max_possible_teams > min_teams:
                    # Show slider when there are multiple options
                    num_teams = st.slider(
                        "Number of Teams",
                        min_value=min_teams,
                        max_value=max_possible_teams,
                        value=min(2, max_possible_teams),
                        help="Choose how many teams to generate"
                    )
                    st.session_state.num_teams = num_teams
                elif max_possible_teams == min_teams:
                    # When min equals max, just set the value and show info
                    num_teams = max_possible_teams
                    st.session_state.num_teams = num_teams
                    st.info(f"🔢 Number of teams: {num_teams} (automatically set based on player count)")
                else:
                    # Fallback case (shouldn't happen with current logic)
                    num_teams = 2
                    st.session_state.num_teams = num_teams
                    st.info(f"🔢 Number of teams: {num_teams} (automatically set)")
            else:
                num_teams = 2
                st.session_state.num_teams = num_teams
                st.info("🔢 Select at least 4 players to configure teams")

            # Calculate optimal team size based on selected players and number of teams
            if selected_count >= 4:
                optimal_team_size = selected_count // num_teams
                leftover_players = selected_count % num_teams
                
                if leftover_players > 0:
                    st.info(f"📊 Optimal team size: {optimal_team_size} ({leftover_players} players will be excluded)")
                else:
                    st.info(f"📊 Optimal team size: {optimal_team_size} (perfect distribution)")
            else:
                st.info("📊 Select at least 4 players to see team size")

            # Show team size slider only when enough players are selected
            if selected_count >= 4:
                # Calculate valid min and max values for slider
                min_team_size = max(1, (selected_count - num_teams) // num_teams)  # Minimum viable team size
                max_team_size = min(8, selected_count // num_teams)  # Maximum reasonable team size

                if min_team_size < max_team_size and max_team_size > 0:
                    team_size = st.slider(
                        "Team Size", 
                        min_value=min_team_size, 
                        max_value=max_team_size, 
                        value=max_team_size,
                        help="Size of each team"
                    )
                    st.session_state.team_size = team_size
                    required_players = team_size * num_teams
                    st.info(f"Required players: {required_players} ({num_teams} teams × {team_size} players)")
                elif min_team_size == max_team_size and max_team_size > 0:
                    # Only one possible team size, set directly and show info
                    team_size = min_team_size
                    st.session_state.team_size = team_size
                    required_players = team_size * num_teams
                    st.info(f"Team size: {team_size} (automatically set)")
                    st.info(f"Required players: {required_players} ({num_teams} teams × {team_size} players)")
                else:
                    # If we can't create a valid slider, just show the calculated team size
                    calculated_team_size = max(1, selected_count // num_teams)
                    st.info(f"📏 Team size: {calculated_team_size} (automatically calculated)")
                    st.session_state.team_size = calculated_team_size
                    required_players = calculated_team_size * num_teams
            else:
                st.session_state.team_size = 0
                required_players = 0
        
        with col2:
            st.markdown("### 📊 Selection Status")
            selected_count = len(st.session_state.selected_players)
            st.metric("Selected Players", f"{selected_count}/{required_players}")
            
            if selected_count >= required_players:
                st.success("✅ Ready to continue!")
            else:
                st.warning(f"⚠️ Need {required_players - selected_count} more players")
        
        # Player selection
        st.markdown("### 👥 Player Selection")
        
        # Convert to DataFrame for selection
        player_data = []
        for player in players:
            player_data.append({
                'ID': player.player_id,
                'Name': player.name,
                'Positions': ', '.join([pos.value for pos in player.positions]),
                'Level': player.stats.level,
                'Stamina': player.stats.stamina,
                'Speed': player.stats.speed,
                'Total': player.stats.level + player.stats.stamina + player.stats.speed
            })
        
        df = pd.DataFrame(player_data)
        
        # Multi-select using player IDs as options
        selected_player_ids = st.multiselect(
            "Select players for teams:",
            options=df['ID'].tolist(),
            format_func=lambda pid: f"{df[df['ID'] == pid]['Name'].iloc[0]} (Level: {df[df['ID'] == pid]['Level'].iloc[0]:.1f}, Total: {df[df['ID'] == pid]['Total'].iloc[0]:.1f})"
        )
        
        # Update selected players
        st.session_state.selected_players = set(selected_player_ids)
        
        # Display selected players
        if st.session_state.selected_players:
            st.markdown("### ✅ Selected Players")
            selected_df = df[df['ID'].isin(st.session_state.selected_players)]
            st.dataframe(selected_df, use_container_width=True, hide_index=True)
        
        # Continue button
        if len(st.session_state.selected_players) >= 4:
            if st.button("Continue → Together Selection", use_container_width=True, type="primary", key="continue_together"):
                st.session_state.current_page = "together"
                st.rerun()
        else:
            st.button("Continue → Together Selection", use_container_width=True, disabled=True, key="continue_together_disabled")
            st.warning("⚠️ Select at least 4 players to continue")
    
    def _show_together_page(self):
        """Show the per-team 'players should play together' page"""
        st.markdown('<h1 class="sub-header">🤝 Players Should Play Together</h1>', unsafe_allow_html=True)
        
        if not st.session_state.selected_players:
            st.error("No players selected. Please go back and select players.")
            return
        
        # Get selected players
        selected_players = [p for p in self.player_registry.get_all_players() 
                          if p.player_id in st.session_state.selected_players]
        
        st.markdown("""
        Select players who should play on the same team for each team.
        You can specify different groups of players for each team.
        """)
        
        # Convert to DataFrame
        player_data = []
        for player in selected_players:
            player_data.append({
                'ID': player.player_id,
                'Name': player.name,
                'Positions': ', '.join([pos.value for pos in player.positions]),
                'Level': player.stats.level,
                'Stamina': player.stats.stamina,
                'Speed': player.stats.speed,
                'Total': player.stats.level + player.stats.stamina + player.stats.speed
            })
        
        df = pd.DataFrame(player_data)
        
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
                
                # Multi-select for this team using player IDs as options
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
                    del st.session_state.per_team_together_constraints[team_number]
        
        # Show summary
        if st.session_state.per_team_together_constraints:
            st.markdown("### 📋 Summary")
            for team_num, player_ids in st.session_state.per_team_together_constraints.items():
                if player_ids:
                    player_names = [df[df['ID'] == pid]['Name'].iloc[0] for pid in player_ids]
                    st.write(f"**Team {team_num}**: {', '.join(player_names)}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True, key="back_together"):
                st.session_state.current_page = "create_teams"
                st.rerun()
        
        with col2:
            if st.button("Continue → Separate Selection", use_container_width=True, key="continue_separate"):
                st.session_state.current_page = "separate"
                st.rerun()
    
    def _show_separate_page(self):
        """Show the 'players should not play together' page"""
        st.markdown('<h1 class="sub-header">🚫 Players Should Not Play Together</h1>', unsafe_allow_html=True)
        
        if not st.session_state.selected_players:
            st.error("No players selected. Please go back and select players.")
            return
        
        # Get selected players
        selected_players = [p for p in self.player_registry.get_all_players() 
                          if p.player_id in st.session_state.selected_players]
        
        st.markdown("""
        Select players who should NOT play on the same team, or skip this step.
        You can select multiple pairs of players who should be separated.
        """)
        
        # Player selection for separate groups
        st.markdown("### 👥 Select Players to Keep Separate")
        
        # Convert to DataFrame
        player_data = []
        for player in selected_players:
            player_data.append({
                'ID': player.player_id,
                'Name': player.name,
                'Positions': ', '.join([pos.value for pos in player.positions]),
                'Level': player.stats.level,
                'Stamina': player.stats.stamina,
                'Speed': player.stats.speed,
                'Total': player.stats.level + player.stats.stamina + player.stats.speed
            })
        
        df = pd.DataFrame(player_data)
        
        # Multi-select for separate players using player IDs as options
        separate_player_ids = st.multiselect(
            "Select players who should NOT play together:",
            options=df['ID'].tolist(),
            format_func=lambda x: f"{df[df['ID'] == x]['Name'].iloc[0]} (Level: {df[df['ID'] == x]['Level'].iloc[0]:.1f})"
        )
        
        # Update separate players
        st.session_state.separate_players = set(separate_player_ids)
        
        # Display separate players
        if st.session_state.separate_players:
            st.markdown("### 🚫 Players Who Will Be Kept Separate")
            separate_players_data = [row for i, row in df.iterrows() if row['ID'] in st.session_state.separate_players]
            separate_df = pd.DataFrame(separate_players_data)
            st.dataframe(separate_df, use_container_width=True, hide_index=True)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.current_page = "create_teams"
                st.rerun()
        
        with col2:
            if st.button("Generate Teams →", use_container_width=True, type="primary", key="generate_teams"):
                self._generate_teams()
    
    def _generate_teams(self):
        """Generate teams and show results"""
        st.markdown('<h1 class="sub-header">⚽ Generating Teams...</h1>', unsafe_allow_html=True)
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Get selected players
            selected_players = [p for p in self.player_registry.get_all_players() 
                              if p.player_id in st.session_state.selected_players]
            
            # Get team configuration from session state
            num_teams = st.session_state.get('num_teams', 2)
            team_size = st.session_state.get('team_size', len(selected_players) // num_teams)
            
            # Validate minimum players
            min_players = num_teams * 2
            if len(selected_players) < min_players:
                st.error(f"Need at least {min_players} players to form {num_teams} teams.")
                return
            
            # Calculate actual team size based on available players and number of teams
            actual_team_size = len(selected_players) // num_teams
            leftover_players = len(selected_players) % num_teams
            
            if leftover_players > 0:
                st.info(f"📊 Forming {num_teams} teams of {actual_team_size} players each from {len(selected_players)} selected players ({leftover_players} players will be excluded)")
            else:
                st.info(f"📊 Forming {num_teams} teams of {actual_team_size} players each from {len(selected_players)} selected players")
            
            # Prepare constraints
            # Prepare per-team constraints
            per_team_together_constraints = {}
            
            # Filter out invalid player IDs that are not in selected players
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
                        per_team_together_constraints[team_num] = [valid_player_ids]
            # Log per-team constraints for debugging
            print(f"   Per-team together constraints: {per_team_together_constraints}")
            together_constraints = []
            separate_constraints = []
            
            # Together constraints (players who should be on same team)
            if st.session_state.together_players:
                together_players = [p for p in selected_players if p.player_id in st.session_state.together_players]
                # Convert to list of player IDs for the config
                together_constraints = [[p.player_id for p in together_players]]
            
            # Separate constraints (players who should not be on same team)
            if st.session_state.separate_players:
                separate_players = [p for p in selected_players if p.player_id in st.session_state.separate_players]
                # Create pairs for separate constraints - convert to player IDs
                for i in range(0, len(separate_players), 2):
                    if i + 1 < len(separate_players):
                        separate_constraints.append([separate_players[i].player_id, separate_players[i + 1].player_id])
                    else:
                        # Handle odd player - add to first group or create single constraint
                        if separate_constraints:
                            separate_constraints[0].append(separate_players[i].player_id)
                        else:
                            separate_constraints.append([separate_players[i].player_id])
            
            # Log constraints for debugging
            print(f"\n🔗 CONSTRAINT ANALYSIS:")
            print(f"   Together players: {[p.name for p in selected_players if p.player_id in st.session_state.together_players]}")
            print(f"   Separate players: {[p.name for p in selected_players if p.player_id in st.session_state.separate_players]}")
            print(f"   Together constraints: {together_constraints}")
            print(f"   Separate constraints: {separate_constraints}")
            
            # Create new team balancer config with dynamic team size and constraints
            dynamic_config = TeamBalancerConfig(
                team_size=actual_team_size,
                num_teams=num_teams,  # Use configured number of teams
                top_n_teams=self.config.top_n_teams,
                diversity_threshold=self.config.diversity_threshold,
                must_be_on_different_teams=separate_constraints,  # Use dynamic separate constraints
                must_be_on_same_teams=together_constraints,       # Use dynamic together constraints
                must_be_on_same_teams_by_team=per_team_together_constraints,
                stat_weights=self.config.stat_weights
            )
            
            # Create new team balancer with dynamic config
            dynamic_balancer = TeamBalancer(dynamic_config, self.player_registry)
            
            # Log selected players
            print(f"\n📋 SELECTED PLAYERS:")
            for player in selected_players:
                print(f"   • {player.name} (Level: {player.stats.level}, Pos: {', '.join([pos.value for pos in player.positions])})")
            
            status_text.text("Preparing team generation...")
            progress_bar.progress(25)
            
            # Prepare constraints
            # Prepare per-team constraints
            per_team_together_constraints = {}
            
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
                    if valid_player_ids:  # Only add non-empty constraints
                        per_team_together_constraints[team_num] = [valid_player_ids]
            
            # Log per-team constraints for debugging
            # Log per-team constraints for debugging
            print(f"   Per-team together constraints: {per_team_together_constraints}")
            together_constraints = []
            separate_constraints = []
            
            # Together constraints (players who should be on same team)
            if st.session_state.together_players:
                together_players = [p for p in selected_players if p.player_id in st.session_state.together_players]
                # Convert to list of player IDs for the config
                together_constraints = [[p.player_id for p in together_players]]
            
            # Separate constraints (players who should not be on same team)
            if st.session_state.separate_players:
                separate_players = [p for p in selected_players if p.player_id in st.session_state.separate_players]
                # Create pairs for separate constraints - convert to player IDs
                for i in range(0, len(separate_players), 2):
                    if i + 1 < len(separate_players):
                        separate_constraints.append([separate_players[i].player_id, separate_players[i + 1].player_id])
            
            status_text.text("Generating team combinations...")
            progress_bar.progress(50)
            
            # Log generation process
            print(f"\n⚽ GENERATING TEAMS")
            print(f"📊 Selected players: {len(selected_players)}")
            print(f"🎯 Team size: {actual_team_size}")
            print(f"🔗 Together constraints: {len(together_constraints)}")
            print(f"🚫 Separate constraints: {len(separate_constraints)}")
            print("-" * 40)
            
            # Generate teams
            print("🔄 Starting team generation...")
            player_ids = [p.player_id for p in selected_players]
            combinations = dynamic_balancer.generate_balanced_teams(player_ids)
            print(f"✅ Team generation complete! Found {len(combinations)} combinations.")
            
            # Print combinations to console
            print(f"\n🏆 TEAM COMBINATIONS GENERATED ({len(combinations)} found)")
            print("=" * 80)
            
            for i, combination in enumerate(combinations[:5]):  # Show top 5 in console
                print(f"\n🎯 COMBINATION #{i+1} (Balance Score: {combination.balance.total_balance_score:.2f})")
                print("-" * 60)
                
                # Display all teams
                team_colors = ["🔵", "🔴", "🟢", "🟡", "🟣", "🟠"]  # Colors for up to 6 teams
                for team_idx, team in enumerate(combination.teams):
                    color = team_colors[team_idx % len(team_colors)]
                    team_total = sum(p.stats.level + p.stats.stamina + p.stats.speed for p in team)
                    print(f"\n{color} TEAM {team_idx + 1} (Total: {team_total:.1f})")
                    for player in team:
                        print(f"   • {player.name} (Level: {player.stats.level}, Pos: {self._format_positions(player)})")
                
                print("-" * 60)
            
            if len(combinations) > 5:
                print(f"... and {len(combinations) - 5} more combinations")
            
            print("=" * 80)
            
            status_text.text("Analyzing results...")
            progress_bar.progress(75)
            
            # Store results in session state
            st.session_state.team_combinations = combinations
            st.session_state.current_page = "results"
            
            status_text.text("Complete!")
            progress_bar.progress(100)
            
            st.success("Teams generated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating teams: {e}")
            progress_bar.empty()
            status_text.empty()
    
    def _show_results_page(self):
        """Show the team generation results"""
        st.markdown('<h1 class="sub-header">🏆 Team Generation Results</h1>', unsafe_allow_html=True)
        
        if 'team_combinations' not in st.session_state:
            st.error("No team combinations found. Please generate teams first.")
            return
        
        combinations = st.session_state.team_combinations
        
        if not combinations:
            st.warning("No valid team combinations found with the given constraints.")
            return
        
        # Display top combinations
        st.markdown(f"### 🏅 Top {min(3, len(combinations))} Team Combinations")
        
        # Add toggle for showing player stats
        show_stats = st.checkbox("Show Player Statistics", value=False, help="Toggle to show/hide detailed player stats")
        
        for i, combination in enumerate(combinations[:3]):
            with st.expander(f"Combination {i+1} - Balance Score: {combination.balance.total_balance_score:.2f}"):
                # Display teams side by side in table format
                self._display_teams_table(combination, i+1, show_stats)
                
                # Display soccer field visualization (optional)
                if st.checkbox(f"Show Field Visualization for Combination {i+1}", value=False):
                    self._display_soccer_field(combination, i+1, show_stats)
                
                # Display detailed stats only if enabled
                if show_stats:
                    # Create columns for each team
                    num_teams = len(combination.teams)
                    team_columns = st.columns(num_teams)
                    
                    team_totals = []
                    team_averages = []
                    
                    for team_idx, (col, team) in enumerate(zip(team_columns, combination.teams)):
                        with col:
                            st.markdown(f"**Team {team_idx + 1}:**")
                            team_players = []
                            for player in team:
                                team_players.append({
                                    'Name': player.name,
                                    'Level': player.stats.level,
                                    'Stamina': player.stats.stamina,
                                    'Speed': player.stats.speed,
                                    'Total': player.stats.level + player.stats.stamina + player.stats.speed
                                })
                            
                            team_df = pd.DataFrame(team_players)
                            st.dataframe(team_df, use_container_width=True, hide_index=True)
                            
                            # Team stats
                            team_avg_level = team_df['Level'].mean()
                            team_avg_stamina = team_df['Stamina'].mean()
                            team_avg_speed = team_df['Speed'].mean()
                            team_total = team_df['Total'].sum()
                            
                            team_totals.append(team_total)
                            team_averages.append({
                                'level': team_avg_level,
                                'stamina': team_avg_stamina,
                                'speed': team_avg_speed
                            })
                            
                            st.metric(f"Team {team_idx + 1} Total", f"{team_total:.1f}")
                    
                    # Balance comparison for multiple teams
                    if num_teams > 1:
                        st.markdown("### ⚖️ Balance Comparison")
                        
                        # Calculate standard deviations for each stat
                        level_values = [avg['level'] for avg in team_averages]
                        stamina_values = [avg['stamina'] for avg in team_averages]
                        speed_values = [avg['speed'] for avg in team_averages]
                        
                        level_std = np.std(level_values) if len(level_values) > 1 else 0
                        stamina_std = np.std(stamina_values) if len(stamina_values) > 1 else 0
                        speed_std = np.std(speed_values) if len(speed_values) > 1 else 0
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Level Balance", f"{level_std:.2f}", help="Lower is better balanced")
                        with col2:
                            st.metric("Stamina Balance", f"{stamina_std:.2f}", help="Lower is better balanced")
                        with col3:
                            st.metric("Speed Balance", f"{speed_std:.2f}", help="Lower is better balanced")
        
        # Export results
        st.markdown("### 📤 Export Results")
        if st.button("Export to JSON", use_container_width=True, key="export_json"):
            self._export_results()
        
        # Navigation
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back to Main", use_container_width=True, key="back_to_main"):
                st.session_state.current_page = "main"
                st.rerun()
        
        with col2:
            if st.button("Generate New Teams", use_container_width=True, type="primary", key="generate_new_teams"):
                st.session_state.current_page = "create_teams"
                st.rerun()
    
    def _display_teams_table(self, combination, combination_number, show_stats=False):
        """Display teams side by side in a table format that can be exported as image"""
        import plotly.graph_objects as go
        import plotly.express as px
        
        # Create data for all teams
        teams_data = []
        num_teams = len(combination.teams)
        
        for team_idx, team in enumerate(combination.teams):
            team_data = []
            for player in team:
                team_data.append({
                    'Player': player.name
                })
            teams_data.append(team_data)
        
        # Calculate team totals (only for display if stats are enabled)
        team_totals = []
        if show_stats:
            for team in combination.teams:
                team_total_level = sum(p.stats.level for p in team)
                team_total_stamina = sum(p.stats.stamina for p in team)
                team_total_speed = sum(p.stats.speed for p in team)
                team_grand_total = team_total_level + team_total_stamina + team_total_speed
                team_totals.append({
                    'level': team_total_level,
                    'stamina': team_total_stamina,
                    'speed': team_total_speed,
                    'grand_total': team_grand_total
                })
        
        # Create table using plotly
        fig = go.Figure()
        
        # Define table layout - only player names
        header_values = ['Player']
        
        # Prepare data for side-by-side display
        # Pad all teams with empty rows to match the longest team
        max_rows = max(len(team_data) for team_data in teams_data) if teams_data else 0
        
        for team_data in teams_data:
            while len(team_data) < max_rows:
                team_data.append({col: '' for col in header_values})
        
        # Create combined header with team labels
        combined_header = []
        for team_idx in range(num_teams):
            team_header = [f'TEAM {team_idx + 1}'] + [''] * (len(header_values) - 1)
            combined_header.extend(team_header)
            if team_idx < num_teams - 1:  # Add separator between teams
                combined_header.append('')
        
        # Create combined data rows
        combined_data = []
        for row_idx in range(max_rows):
            row_data = []
            for team_idx, team_data in enumerate(teams_data):
                for col in header_values:
                    row_data.append(team_data[row_idx][col])
                if team_idx < num_teams - 1:  # Add separator between teams
                    row_data.append('')
            combined_data.append(row_data)
        
        # Transpose data for plotly table
        table_data = list(zip(*combined_data)) if combined_data else []
        
        # Create alternating colors for teams
        team_colors = ['#E3F2FD', '#FFEBEE', '#E8F5E8', '#FFF3E0', '#F3E5F5', '#E0F2F1']
        cell_colors = []
        for team_idx in range(num_teams):
            color = team_colors[team_idx % len(team_colors)]
            cell_colors.extend([color] * len(header_values))
            if team_idx < num_teams - 1:  # Add separator color
                cell_colors.append('#FFFFFF')
        
        # Add table to figure
        fig.add_trace(go.Table(
            header=dict(
                values=combined_header,
                fill_color='#1f77b4',
                font=dict(color='white', size=14, family='Arial Black'),
                align='center',
                height=40
            ),
            cells=dict(
                values=table_data,
                fill_color=[cell_colors * max_rows] if cell_colors else [],
                font=dict(size=12, family='Arial'),
                align='center',
                height=35
            )
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Team Combination {combination_number}",
            title_x=0.5,
            width=min(800, 200 * num_teams),  # Adjust width based on number of teams
            height=50 + max_rows * 35,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial", size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display team stats summary if enabled
        if show_stats and team_totals:
            st.markdown("#### Team Statistics Summary")
            stats_cols = st.columns(num_teams)
            
            for team_idx, (col, totals) in enumerate(zip(stats_cols, team_totals)):
                with col:
                    st.metric(f"Team {team_idx + 1} Total", f"{totals['grand_total']:.1f}")
                    st.caption(f"Level: {totals['level']:.1f} | Stamina: {totals['stamina']:.1f} | Speed: {totals['speed']:.1f}")

    def _display_soccer_field(self, combination, combination_number, show_stats=False):
        """Display teams on a soccer field visualization"""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create soccer field coordinates
        field_width = 100
        field_height = 60
        
        # Field markings
        field_lines = {
            'center_line': [(50, 0), (50, 60)],
            'center_circle': [(50, 30), 9],  # center, radius
            'penalty_box_left': [(0, 15), (16, 45)],  # top-left, bottom-right
            'penalty_box_right': [(84, 15), (100, 45)],
            'goal_area_left': [(0, 25), (5, 35)],
            'goal_area_right': [(95, 25), (100, 35)]
        }

        # Create figure
        fig = go.Figure()

        # Add simple background (no pitch drawing)
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=field_width, y1=field_height,
            fillcolor="white",
            line=dict(color="lightgray", width=1),
            layer="below"
        )

        # Position players on the field
        team_a_positions = self._get_player_positions(combination.team1, 'left')
        team_b_positions = self._get_player_positions(combination.team2, 'right')

        # Add Team A players (left side - red/orange)
        for player in combination.team1:
            if player.name in team_a_positions:
                pos = team_a_positions[player.name]

                # Truncate long names for display
                display_name = player.name[:12] + "..." if len(player.name) > 12 else player.name

                # Create hover text with player stats if enabled
                if show_stats:
                    hover_text = f"""
                    <b>{player.name}</b><br>
                    Position: {', '.join([p.value for p in player.positions])}<br>
                    Level: {player.stats.level}<br>
                    Stamina: {player.stats.stamina}<br>
                    Speed: {player.stats.speed}<br>
                    Total: {player.stats.level + player.stats.stamina + player.stats.speed:.1f}
                    """
                    hover_info = 'text'
                    hovertemplate = hover_text
                else:
                    hover_info = 'skip'
                    hovertemplate = None

                fig.add_trace(go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode='markers+text',
                    marker=dict(
                        size=25,
                        color='red',
                        symbol='circle',
                        line=dict(color='darkred', width=2)
                    ),
                    text=[display_name],
                    textposition='bottom center',
                    textfont=dict(size=10, color='black'),
                    name=f'Team A - {player.name}',
                    showlegend=False,
                    hoverinfo=hover_info,
                    hovertemplate=hovertemplate
                ))

        # Add Team B players (right side - blue)
        for player in combination.team2:
            if player.name in team_b_positions:
                pos = team_b_positions[player.name]

                # Truncate long names for display
                display_name = player.name[:12] + "..." if len(player.name) > 12 else player.name

                # Create hover text with player stats if enabled
                if show_stats:
                    hover_text = f"""
                    <b>{player.name}</b><br>
                    Position: {', '.join([p.value for p in player.positions])}<br>
                    Level: {player.stats.level}<br>
                    Stamina: {player.stats.stamina}<br>
                    Speed: {player.stats.speed}<br>
                    Total: {player.stats.level + player.stats.stamina + player.stats.speed:.1f}
                    """
                    hover_info = 'text'
                    hovertemplate = hover_text
                else:
                    hover_info = 'skip'
                    hovertemplate = None

                fig.add_trace(go.Scatter(
                    x=[pos[0]],
                    y=[pos[1]],
                    mode='markers+text',
                    marker=dict(
                        size=25,
                        color='blue',
                        symbol='circle',
                        line=dict(color='darkblue', width=2)
                    ),
                    text=[display_name],
                    textposition='bottom center',
                    textfont=dict(size=10, color='black'),
                    name=f'Team B - {player.name}',
                    showlegend=False,
                    hoverinfo=hover_info,
                    hovertemplate=hovertemplate
                ))

        # Update layout for screenshot-friendly design
        fig.update_layout(
            title=f"Team Combination {combination_number}",
            xaxis=dict(
                range=[0, field_width],
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            yaxis=dict(
                range=[0, field_height],
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=900,
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
            font=dict(family="Arial", size=12)
        )

        # Add team labels with better styling
        fig.add_annotation(
            x=25, y=55,
            text="TEAM A",
            showarrow=False,
            font=dict(size=18, color='red', family="Arial, sans-serif"),
            bgcolor='white',
            bordercolor='red',
            borderwidth=3,
            xanchor='center',
            yanchor='middle'
        )

        fig.add_annotation(
            x=75, y=55,
            text="TEAM B",
            showarrow=False,
            font=dict(size=18, color='blue', family="Arial, sans-serif"),
            borderwidth=3,
            xanchor='center',
            yanchor='middle'
        )

        # Adjust for more teams (C, D, E, F)
        if num_teams > 2:
            fig.add_annotation(
                x=10, y=45,
                text="TEAM C",
                showarrow=False,
                font=dict(size=16, color='green', family="Arial, sans-serif"),
                bgcolor='white',
                bordercolor='green',
                borderwidth=2,
                xanchor='center',
                yanchor='middle'
            )

            fig.add_annotation(
                x=90, y=45,
                text="TEAM D",
                showarrow=False,
                font=dict(size=16, color='orange', family="Arial, sans-serif"),
                bgcolor='white',
                bordercolor='orange',
                borderwidth=2,
                xanchor='center',
                yanchor='middle'
            )

        if num_teams > 4:
            fig.add_annotation(
                x=10, y=35,
                text="TEAM E",
                showarrow=False,
                font=dict(size=16, color='purple', family="Arial, sans-serif"),
                bgcolor='white',
                bordercolor='purple',
                borderwidth=2,
                xanchor='center',
                yanchor='middle'
            )

            fig.add_annotation(
                x=90, y=35,
                text="TEAM F",
                showarrow=False,
                font=dict(size=16, color='brown', family="Arial, sans-serif"),
                bgcolor='white',
                bordercolor='brown',
                borderwidth=2,
                xanchor='center',
                yanchor='middle'
            )

        # Hide axes
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        # Add field markings
        for line, (start, end) in field_lines.items():
            if line == 'center_circle':
                # Center circle (draw as a circle)
                fig.add_shape(
                    type="circle",
                    xref="x", yref="y",
                    x0=start[0]-end, y0=start[1]-end,
                    x1=start[0]+end, y1=start[1]+end,
                    line_color="black",
                    fillcolor="rgba(255, 255, 255, 0.5)",
                    layer="above"
                )
            else:
                # Other lines (rectangles)
                fig.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=start[0], y0=start[1],
                    x1=end[0], y1=end[1],
                    line_color="black",
                    fillcolor="rgba(255, 255, 255, 0.5)",
                    layer="above"
                )

        # Update layout
        fig.update_layout(
            title=f"Team Combination {combination_number} - {num_teams} Teams",
            title_x=0.5,
            width=800,
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial, sans-serif", size=12)
        )

        st.plotly_chart(fig, use_container_width=True)

    def _get_player_positions(self, team_players, side):
        """Get positions for players on the soccer field based on their positions with smart distribution"""
        positions = {}

        # Define position mappings for each side with multiple slots per position
        if side == 'left':
            # Team A positions (left side) - multiple slots per position
            position_slots = {
                'FW': [(10, 30), (12, 25), (12, 35)],      # Forward positions
                'LW': [(8, 20), (10, 15), (6, 25)],        # Left wing positions
                'RW': [(8, 40), (10, 45), (6, 35)],        # Right wing positions
                'CM': [(25, 30), (28, 25), (28, 35)],      # Center mid positions
                'MF': [(25, 30), (28, 25), (28, 35)],      # Midfielder positions
                'DF': [(15, 30), (18, 25), (18, 35)],      # Defender positions
                'CB': [(15, 30), (18, 25), (18, 35)],      # Center back positions
                'LB': [(15, 15), (18, 10), (12, 20)],      # Left back positions
                'RB': [(15, 45), (18, 50), (12, 40)],      # Right back positions
                'GK': [(5, 30), (3, 25), (3, 35)],         # Goalkeeper positions
            }
        else:
            # Team B positions (right side) - multiple slots per position
            position_slots = {
                'FW': [(90, 30), (88, 25), (88, 35)],      # Forward positions
                'LW': [(92, 20), (90, 15), (94, 25)],      # Left wing positions
                'RW': [(92, 40), (90, 45), (94, 35)],      # Right wing positions
                'CM': [(75, 30), (72, 25), (72, 35)],      # Center mid positions
                'MF': [(75, 30), (72, 25), (72, 35)],      # Midfielder positions
                'DF': [(85, 30), (82, 25), (82, 35)],      # Defender positions
                'CB': [(85, 30), (82, 25), (82, 35)],      # Center back positions
                'LB': [(85, 15), (82, 10), (88, 20)],      # Left back positions
                'RB': [(85, 45), (82, 50), (88, 40)],      # Right back positions
                'GK': [(95, 30), (97, 25), (97, 35)],      # Goalkeeper positions
            }

        # Position priority order (closest to forward)
        position_priority = ['FW', 'LW', 'RW', 'CM', 'MF', 'DF', 'CB', 'LB', 'RB', 'GK']

        # Track used coordinates to avoid overlap
        used_coords = set()

        # First pass: assign players to their primary positions
        for player in team_players:
            primary_pos = player.positions[0].value if player.positions else 'MF'

            if primary_pos in position_slots:
                # Try to find an available slot for this position
                for coords in position_slots[primary_pos]:
                    if coords not in used_coords:
                        positions[player.name] = coords
                        used_coords.add(coords)
                        break
                else:
                    # All slots for this position are used, mark for secondary assignment
                    positions[player.name] = None
            else:
                # Position not found, mark for secondary assignment
                positions[player.name] = None

        # Second pass: assign remaining players to closest available positions
        remaining_players = [name for name, pos in positions.items() if pos is None]

        for player_name in remaining_players:
            player = next(p for p in team_players if p.name == player_name)
            primary_pos = player.positions[0].value if player.positions else 'MF'

            # Find closest available position based on priority
            assigned = False

            # Try positions in priority order
            for pos in position_priority:
                if pos in position_slots:
                    for coords in position_slots[pos]:
                        if coords not in used_coords:
                            positions[player_name] = coords
                            used_coords.add(coords)
                            assigned = True
                            break
                    if assigned:
                        break

            # If still not assigned, find any available position
            if not assigned:
                for pos, slots in position_slots.items():
                    for coords in slots:
                        if coords not in used_coords:
                            positions[player_name] = coords
                            used_coords.add(coords)
                            assigned = True
                            break
                    if assigned:
                        break

            # Last resort: create a new position near the center
            if not assigned:
                if side == 'left':
                    x_base, y_base = 20, 30
                else:
                    x_base, y_base = 80, 30

                # Find a free spot with some offset
                offset = len(used_coords) * 2
                new_coords = (x_base + offset, y_base + (offset % 8))

                positions[player_name] = new_coords
                used_coords.add(new_coords)

        return positions

    def _export_results(self):
        """Export results to JSON - supports multiple teams"""
        if 'team_combinations' not in st.session_state:
            st.error("No results to export.")
            return

        try:
            # Prepare export data
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'team_size': st.session_state.team_size,
                'num_teams': st.session_state.get('num_teams', 2),
                'total_players': len(st.session_state.selected_players),
                'combinations': []
            }

            for i, combination in enumerate(st.session_state.team_combinations[:3]):
                combo_data = {
                    'rank': i + 1,
                    'balance_score': combination.balance.total_balance_score,
                    'teams': []
                }

                # Export all teams, not just team_a and team_b
                for team_idx, team in enumerate(combination.teams):
                    team_data = {
                        'team_id': team_idx + 1,
                        'players': [
                            {
                                'name': p.name,
                                'level': p.stats.level,
                                'stamina': p.stats.stamina,
                                'speed': p.stats.speed,
                                'positions': [pos.value for pos in p.positions],
                                'total_stats': p.stats.level + p.stats.stamina + p.stats.speed
                            }
                            for p in team
                        ],
                        'team_totals': {
                            'level': sum(p.stats.level for p in team),
                            'stamina': sum(p.stats.stamina for p in team),
                            'speed': sum(p.stats.speed for p in team),
                            'total': sum(p.stats.level + p.stats.stamina + p.stats.speed for p in team)
                        }
                    }
                    combo_data['teams'].append(team_data)

                export_data['combinations'].append(combo_data)
            
            # Create download button
            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                label="Download Results JSON",
                data=json_str,
                file_name=f"team_combinations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("Results exported successfully!")
            
        except Exception as e:
            st.error(f"Error exporting results: {e}")


def main():
    """Main function to run the Streamlit app"""
    app = StreamlitTeamBalancerUI()
    app.run()


if __name__ == "__main__":
    main()
