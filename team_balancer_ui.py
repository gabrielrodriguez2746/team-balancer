#!/usr/bin/env python3
"""
Modern Team Balancer UI with Multi-Screen Workflow
Provides a user-friendly interface for team balancing and player management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional, Set
import logging
import threading
import time
from pathlib import Path

from team_balancer import Player, TeamBalancer, TeamBalancerConfig, PlayerRegistry, TeamBalancerDisplay, Position, PlayerStats
from config import AppConfig
from data_manager import DataManager

logger = logging.getLogger(__name__)

class PlayerDialog:
    """Dialog for creating/editing players"""
    
    def __init__(self, parent, player: Optional[Player] = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Player" if player else "Add New Player")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.player = player
        self.result = None
        
        self._setup_ui()
        self._populate_data()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"400x500+{x}+{y}")
        
        # Focus on name entry
        self.name_entry.focus()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = "Edit Player" if self.player else "Add New Player"
        title_label = ttk.Label(main_frame, text=title, style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Name field
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(name_frame, text="Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Positions field
        pos_frame = ttk.Frame(main_frame)
        pos_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(pos_frame, text="Positions:").pack(anchor=tk.W)
        
        # Position checkboxes
        self.position_vars = {}
        positions = [pos.value for pos in Position]
        pos_check_frame = ttk.Frame(pos_frame)
        pos_check_frame.pack(fill=tk.X, pady=(5, 0))
        
        for i, pos in enumerate(positions):
            var = tk.BooleanVar()
            self.position_vars[pos] = var
            cb = ttk.Checkbutton(pos_check_frame, text=pos, variable=var)
            cb.grid(row=i//3, column=i%3, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Level
        level_frame = ttk.Frame(stats_frame)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(level_frame, text="Level (1.0-5.0):").pack(side=tk.LEFT)
        self.level_var = tk.DoubleVar(value=3.0)
        self.level_scale = ttk.Scale(level_frame, from_=1.0, to=5.0, variable=self.level_var, orient=tk.HORIZONTAL)
        self.level_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.level_label = ttk.Label(level_frame, text="3.0")
        self.level_label.pack(side=tk.RIGHT, padx=(10, 0))
        self.level_scale.configure(command=self._update_level_label)
        
        # Stamina
        stamina_frame = ttk.Frame(stats_frame)
        stamina_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(stamina_frame, text="Stamina (1.0-5.0):").pack(side=tk.LEFT)
        self.stamina_var = tk.DoubleVar(value=3.0)
        self.stamina_scale = ttk.Scale(stamina_frame, from_=1.0, to=5.0, variable=self.stamina_var, orient=tk.HORIZONTAL)
        self.stamina_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.stamina_label = ttk.Label(stamina_frame, text="3.0")
        self.stamina_label.pack(side=tk.RIGHT, padx=(10, 0))
        self.stamina_scale.configure(command=self._update_stamina_label)
        
        # Speed
        speed_frame = ttk.Frame(stats_frame)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(speed_frame, text="Speed (1.0-5.0):").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=3.0)
        self.speed_scale = ttk.Scale(speed_frame, from_=1.0, to=5.0, variable=self.speed_var, orient=tk.HORIZONTAL)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        self.speed_label = ttk.Label(speed_frame, text="3.0")
        self.speed_label.pack(side=tk.RIGHT, padx=(10, 0))
        self.speed_scale.configure(command=self._update_speed_label)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.save_btn = ttk.Button(button_frame, text="Save", command=self._save, style='Primary.TButton')
        self.save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self._save())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _update_level_label(self, value):
        self.level_label.config(text=f"{float(value):.1f}")
    
    def _update_stamina_label(self, value):
        self.stamina_label.config(text=f"{float(value):.1f}")
    
    def _update_speed_label(self, value):
        self.speed_label.config(text=f"{float(value):.1f}")
    
    def _populate_data(self):
        """Populate dialog with existing player data"""
        if self.player:
            self.name_entry.insert(0, self.player.name)
            
            # Set positions
            for pos in self.player.positions:
                if pos.value in self.position_vars:
                    self.position_vars[pos.value].set(True)
            
            # Set stats
            self.level_var.set(self.player.stats.level)
            self.stamina_var.set(self.player.stats.stamina)
            self.speed_var.set(self.player.stats.speed)
            
            # Update labels
            self._update_level_label(self.player.stats.level)
            self._update_stamina_label(self.player.stats.stamina)
            self._update_speed_label(self.player.stats.speed)
    
    def _validate(self) -> bool:
        """Validate form data"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Player name is required")
            self.name_entry.focus()
            return False
        
        # Check if at least one position is selected
        selected_positions = [pos for pos, var in self.position_vars.items() if var.get()]
        if not selected_positions:
            messagebox.showerror("Error", "At least one position must be selected")
            return False
        
        return True
    
    def _save(self):
        """Save player data"""
        if not self._validate():
            return
        
        try:
            name = self.name_entry.get().strip()
            selected_positions = [Position(pos) for pos, var in self.position_vars.items() if var.get()]
            
            stats = PlayerStats(
                level=self.level_var.get(),
                stamina=self.stamina_var.get(),
                speed=self.speed_var.get()
            )
            
            if self.player:
                # Update existing player
                self.player.name = name
                self.player.positions = selected_positions
                self.player.stats = stats
                self.result = self.player
            else:
                # Create new player
                self.result = Player(
                    name=name,
                    positions=selected_positions,
                    stats=stats
                )
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save player: {e}")
    
    def _cancel(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()

class ModernTeamBalancerUI:
    """Modern team balancer user interface with multi-screen workflow"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Team Balancer Pro")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.config = AppConfig.load()
        self.data_manager = DataManager(self.config)
        self.player_registry = PlayerRegistry()
        self.team_balancer = TeamBalancer(TeamBalancerConfig(), self.player_registry)
        
        # UI state
        self.current_screen = "main"
        self.selected_players: Set[int] = set()
        self.team_size = 6
        self.must_be_together: List[List[int]] = []
        self.must_be_separate: List[List[int]] = []
        
        # Loading state
        self.is_loading = False
        self.loading_thread = None
        
        # Load players
        self._load_players()
        
        # Setup UI
        self._setup_ui()
        self._setup_styles()
        
        # Show main screen
        self._show_main_screen()
        
    def _load_players(self):
        """Load players from data source"""
        try:
            players = self.data_manager.load_players()
            if not players:
                logger.error("No players found in data/players.json")
                messagebox.showerror("Error", "No player data found. Please ensure data/players.json exists and contains valid player data.")
                return
            else:
                # Load into registry
                for player in players:
                    self.player_registry.add_player(player)
        except Exception as e:
            logger.error(f"Error loading players: {e}")
            messagebox.showerror("Error", f"Failed to load players: {e}")
    
    def _setup_styles(self):
        """Setup modern UI styles"""
        style = ttk.Style()
        
        # Configure styles
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Arial', 12, 'bold'))
        style.configure('Secondary.TButton', font=('Arial', 10))
        style.configure('Danger.TButton', font=('Arial', 10))
        style.configure('Large.TButton', font=('Arial', 14, 'bold'))
    
    def _setup_ui(self):
        """Setup the main UI components"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Title
        self.title_label = ttk.Label(self.main_frame, text="Team Balancer Pro", style='Title.TLabel')
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Status bar
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def _clear_content(self):
        """Clear the content frame"""
        # Clear button references to prevent stale references
        self._clear_button_references()
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _clear_button_references(self):
        """Clear button references to prevent stale widget access"""
        # Clear player management buttons
        if hasattr(self, 'add_btn'):
            delattr(self, 'add_btn')
        if hasattr(self, 'edit_btn'):
            delattr(self, 'edit_btn')
        if hasattr(self, 'delete_btn'):
            delattr(self, 'delete_btn')
        if hasattr(self, 'refresh_btn'):
            delattr(self, 'refresh_btn')
        
        # Clear team creation buttons
        if hasattr(self, 'continue_btn'):
            delattr(self, 'continue_btn')
        
        # Clear tree references
        if hasattr(self, 'player_tree'):
            delattr(self, 'player_tree')
        if hasattr(self, 'selection_tree'):
            delattr(self, 'selection_tree')
        if hasattr(self, 'together_tree'):
            delattr(self, 'together_tree')
        if hasattr(self, 'separate_tree'):
            delattr(self, 'separate_tree')
    
    def _show_loading(self, message: str = "Loading..."):
        """Show loading indicator"""
        self.is_loading = True
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=f"⏳ {message}")
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
            self.progress_bar.start()
            self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        self.root.update()
    
    def _hide_loading(self, message: str = "Ready"):
        """Hide loading indicator"""
        self.is_loading = False
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message)
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
        self.root.update()
    
    def _reset_loading_state(self):
        """Reset loading state in case it gets stuck"""
        self.is_loading = False
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text="Ready")
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
        self._enable_buttons()
    
    def _disable_buttons(self):
        """Disable all buttons during operations"""
        if self.current_screen == "players":
            if hasattr(self, 'add_btn') and self.add_btn.winfo_exists():
                self.add_btn.config(state='disabled')
            if hasattr(self, 'edit_btn') and self.edit_btn.winfo_exists():
                self.edit_btn.config(state='disabled')
            if hasattr(self, 'delete_btn') and self.delete_btn.winfo_exists():
                self.delete_btn.config(state='disabled')
            if hasattr(self, 'refresh_btn') and self.refresh_btn.winfo_exists():
                self.refresh_btn.config(state='disabled')
        elif self.current_screen == "create_teams":
            if hasattr(self, 'continue_btn') and self.continue_btn.winfo_exists():
                self.continue_btn.config(state='disabled')
    
    def _enable_buttons(self):
        """Enable all buttons after operations"""
        if self.current_screen == "players":
            if hasattr(self, 'add_btn') and self.add_btn.winfo_exists():
                self.add_btn.config(state='normal')
            if hasattr(self, 'edit_btn') and self.edit_btn.winfo_exists():
                self.edit_btn.config(state='normal')
            if hasattr(self, 'delete_btn') and self.delete_btn.winfo_exists():
                self.delete_btn.config(state='normal')
            if hasattr(self, 'refresh_btn') and self.refresh_btn.winfo_exists():
                self.refresh_btn.config(state='normal')
            # Update button states based on current selection
            self._update_player_buttons()
        elif self.current_screen == "create_teams":
            if hasattr(self, 'continue_btn') and self.continue_btn.winfo_exists():
                # Re-enable based on selection
                required_players = self.team_size_var.get() * 2
                selected_count = len(self.selected_players)
                if selected_count >= required_players:
                    self.continue_btn.config(state='normal')
                else:
                    self.continue_btn.config(state='disabled')
    
    def _update_player_buttons(self):
        """Update player management button states based on selection"""
        if self.current_screen != "players":
            return
        
        selected_count = len(self.selected_players)
        
        # Edit button: enabled only when exactly one player is selected
        if hasattr(self, 'edit_btn') and self.edit_btn.winfo_exists():
            if selected_count == 1:
                self.edit_btn.config(state='normal')
            else:
                self.edit_btn.config(state='disabled')
        
        # Delete button: enabled when at least one player is selected
        if hasattr(self, 'delete_btn') and self.delete_btn.winfo_exists():
            if selected_count > 0:
                self.delete_btn.config(state='normal')
            else:
                self.delete_btn.config(state='disabled')
    
    def _run_with_loading(self, operation, loading_message: str = "Processing...", success_message: str = "Ready"):
        """Run an operation with loading indicator"""
        # For team generation, run in thread
        if 'generate' in loading_message.lower():
            def run_operation():
                try:
                    self.root.after(0, lambda: self._show_loading(loading_message))
                    self.root.after(0, lambda: self._disable_buttons())
                    result = operation()
                    self.root.after(0, lambda: self._hide_loading(success_message))
                    self.root.after(0, lambda: self._enable_buttons())
                    return result
                except Exception as e:
                    self.root.after(0, lambda: self._hide_loading(f"Error: {str(e)}"))
                    self.root.after(0, lambda: self._enable_buttons())
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                    raise e
            
            self.loading_thread = threading.Thread(target=run_operation)
            self.loading_thread.daemon = True
            self.loading_thread.start()
        else:
            # For quick operations, run directly without loading state
            try:
                result = operation()
                return result
            except Exception as e:
                messagebox.showerror("Error", str(e))
                raise e
    
    def _show_main_screen(self):
        """Show the main menu screen"""
        self.current_screen = "main"
        self._reset_loading_state()
        self._clear_content()
        
        # Main menu buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(expand=True)
        
        # See Players button
        see_players_btn = ttk.Button(button_frame, text="👥 See Players", 
                                   command=self._show_players_screen, style='Large.TButton')
        see_players_btn.pack(pady=20, ipadx=40, ipady=10)
        
        # Create Teams button
        create_teams_btn = ttk.Button(button_frame, text="⚽ Create Teams", 
                                    command=self._show_create_teams_screen, style='Large.TButton')
        create_teams_btn.pack(pady=20, ipadx=40, ipady=10)
        
        # Update status
        self.status_label.config(text="Main Menu - Ready")
    
    def _show_players_screen(self):
        """Show the players management screen"""
        self.current_screen = "players"
        self._reset_loading_state()
        self._clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Player Management", style='Subtitle.TLabel').pack(side=tk.LEFT)
        
        # Back button
        back_btn = ttk.Button(header_frame, text="← Back to Main", command=self._show_main_screen)
        back_btn.pack(side=tk.RIGHT)
        
        # CRUD buttons
        crud_frame = ttk.Frame(self.content_frame)
        crud_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.add_btn = ttk.Button(crud_frame, text="➕ Add Player", command=self._add_player, style='Primary.TButton')
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_btn = ttk.Button(crud_frame, text="✏️ Edit Player", command=self._edit_player, style='Secondary.TButton')
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_btn = ttk.Button(crud_frame, text="🗑️ Delete Player", command=self._delete_player, style='Danger.TButton')
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(crud_frame, text="🔄 Refresh", command=self._refresh_players, style='Secondary.TButton')
        self.refresh_btn.pack(side=tk.LEFT)
        
        # Player count
        player_count = len(self.player_registry.get_all_players())
        count_label = ttk.Label(crud_frame, text=f"Total Players: {player_count}", style='Header.TLabel')
        count_label.pack(side=tk.RIGHT)
        
        # Player list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('ID', 'Name', 'Positions', 'Level', 'Stamina', 'Speed')
        self.player_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.player_tree.heading('#0', text='Select')
        self.player_tree.column('#0', width=50, stretch=False)
        self.player_tree.heading('ID', text='ID')
        self.player_tree.column('ID', width=40, stretch=False)
        self.player_tree.heading('Name', text='Name')
        self.player_tree.column('Name', width=150)
        self.player_tree.heading('Positions', text='Positions')
        self.player_tree.column('Positions', width=100)
        self.player_tree.heading('Level', text='Level')
        self.player_tree.column('Level', width=60)
        self.player_tree.heading('Stamina', text='Stamina')
        self.player_tree.column('Stamina', width=60)
        self.player_tree.heading('Speed', text='Speed')
        self.player_tree.column('Speed', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.player_tree.yview)
        self.player_tree.configure(yscrollcommand=scrollbar.set)
        
        self.player_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.player_tree.bind('<<TreeviewSelect>>', self._on_player_select)
        self.player_tree.bind('<Double-1>', self._on_player_double_click)
        
        # Populate list
        self._populate_player_list()
        
        # Initialize button states
        self._update_player_buttons()
        
        # Update status
        self.status_label.config(text=f"Player Management - {player_count} players")
    
    def _show_create_teams_screen(self):
        """Show the team creation screen"""
        self.current_screen = "create_teams"
        self._reset_loading_state()
        self._clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Create Teams", style='Subtitle.TLabel').pack(side=tk.LEFT)
        
        # Back button
        back_btn = ttk.Button(header_frame, text="← Back to Main", command=self._show_main_screen)
        back_btn.pack(side=tk.RIGHT)
        
        # Team size selection
        size_frame = ttk.LabelFrame(self.content_frame, text="Team Configuration", padding="10")
        size_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(size_frame, text="Team Size:").pack(side=tk.LEFT)
        self.team_size_var = tk.IntVar(value=6)
        size_spinbox = ttk.Spinbox(size_frame, from_=3, to=12, textvariable=self.team_size_var, width=10)
        size_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Player selection info
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selection_label = ttk.Label(info_frame, text="Select 0 players", style='Header.TLabel')
        self.selection_label.pack(side=tk.LEFT)
        
        # Continue button
        self.continue_btn = ttk.Button(info_frame, text="Continue →", command=self._show_together_screen, 
                                     style='Primary.TButton', state='disabled')
        self.continue_btn.pack(side=tk.RIGHT)
        
        # Player selection list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for selection
        columns = ('ID', 'Name', 'Positions', 'Level', 'Stamina', 'Speed')
        self.selection_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.selection_tree.heading('#0', text='Select')
        self.selection_tree.column('#0', width=50, stretch=False)
        self.selection_tree.heading('ID', text='ID')
        self.selection_tree.column('ID', width=40, stretch=False)
        self.selection_tree.heading('Name', text='Name')
        self.selection_tree.column('Name', width=150)
        self.selection_tree.heading('Positions', text='Positions')
        self.selection_tree.column('Positions', width=100)
        self.selection_tree.heading('Level', text='Level')
        self.selection_tree.column('Level', width=60)
        self.selection_tree.heading('Stamina', text='Stamina')
        self.selection_tree.column('Stamina', width=60)
        self.selection_tree.heading('Speed', text='Speed')
        self.selection_tree.column('Speed', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.selection_tree.yview)
        self.selection_tree.configure(yscrollcommand=scrollbar.set)
        
        self.selection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.selection_tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        
        # Populate selection list
        self._populate_selection_list()
        
        # Update status
        self.status_label.config(text="Create Teams - Select players")
    
    def _show_together_screen(self):
        """Show the 'players should play together' screen"""
        self.current_screen = "together"
        self._clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Players Should Play Together", style='Subtitle.TLabel').pack(side=tk.LEFT)
        
        # Back button
        back_btn = ttk.Button(header_frame, text="← Back", command=self._show_create_teams_screen)
        back_btn.pack(side=tk.RIGHT)
        
        # Instructions
        instructions = ttk.Label(self.content_frame, text="Select players who should play on the same team, or skip this step.", 
                               style='Header.TLabel')
        instructions.pack(pady=(0, 20))
        
        # Selected players info
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.together_label = ttk.Label(info_frame, text=f"Selected: {len(self.selected_players)} players", style='Header.TLabel')
        self.together_label.pack(side=tk.LEFT)
        
        # Navigation buttons
        skip_btn = ttk.Button(info_frame, text="Skip →", command=self._show_separate_screen, style='Secondary.TButton')
        skip_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        continue_btn = ttk.Button(info_frame, text="Continue →", command=self._show_separate_screen, 
                                style='Primary.TButton')
        continue_btn.pack(side=tk.RIGHT)
        
        # Player selection list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for together selection
        columns = ('ID', 'Name', 'Positions', 'Level', 'Stamina', 'Speed')
        self.together_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.together_tree.heading('#0', text='Select')
        self.together_tree.column('#0', width=50, stretch=False)
        self.together_tree.heading('ID', text='ID')
        self.together_tree.column('ID', width=40, stretch=False)
        self.together_tree.heading('Name', text='Name')
        self.together_tree.column('Name', width=150)
        self.together_tree.heading('Positions', text='Positions')
        self.together_tree.column('Positions', width=100)
        self.together_tree.heading('Level', text='Level')
        self.together_tree.column('Level', width=60)
        self.together_tree.heading('Stamina', text='Stamina')
        self.together_tree.column('Stamina', width=60)
        self.together_tree.heading('Speed', text='Speed')
        self.together_tree.column('Speed', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.together_tree.yview)
        self.together_tree.configure(yscrollcommand=scrollbar.set)
        
        self.together_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.together_tree.bind('<<TreeviewSelect>>', self._on_together_select)
        
        # Populate together list
        self._populate_together_list()
        
        # Update status
        self.status_label.config(text="Together Selection - Choose players who should play together")
    
    def _show_separate_screen(self):
        """Show the 'players should not play together' screen"""
        self.current_screen = "separate"
        self._clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Players Should Not Play Together", style='Subtitle.TLabel').pack(side=tk.LEFT)
        
        # Back button
        back_btn = ttk.Button(header_frame, text="← Back", command=self._show_together_screen)
        back_btn.pack(side=tk.RIGHT)
        
        # Instructions
        instructions = ttk.Label(self.content_frame, text="Select players who should NOT play on the same team, or skip this step.", 
                               style='Header.TLabel')
        instructions.pack(pady=(0, 20))
        
        # Selected players info
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.separate_label = ttk.Label(info_frame, text=f"Selected: {len(self.selected_players)} players", style='Header.TLabel')
        self.separate_label.pack(side=tk.LEFT)
        
        # Navigation buttons
        skip_btn = ttk.Button(info_frame, text="Skip →", command=self._generate_teams, style='Secondary.TButton')
        skip_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        continue_btn = ttk.Button(info_frame, text="Generate Teams →", command=self._generate_teams, 
                                style='Primary.TButton')
        continue_btn.pack(side=tk.RIGHT)
        
        # Player selection list
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for separate selection
        columns = ('ID', 'Name', 'Positions', 'Level', 'Stamina', 'Speed')
        self.separate_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.separate_tree.heading('#0', text='Select')
        self.separate_tree.column('#0', width=50, stretch=False)
        self.separate_tree.heading('ID', text='ID')
        self.separate_tree.column('ID', width=40, stretch=False)
        self.separate_tree.heading('Name', text='Name')
        self.separate_tree.column('Name', width=150)
        self.separate_tree.heading('Positions', text='Positions')
        self.separate_tree.column('Positions', width=100)
        self.separate_tree.heading('Level', text='Level')
        self.separate_tree.column('Level', width=60)
        self.separate_tree.heading('Stamina', text='Stamina')
        self.separate_tree.column('Stamina', width=60)
        self.separate_tree.heading('Speed', text='Speed')
        self.separate_tree.column('Speed', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.separate_tree.yview)
        self.separate_tree.configure(yscrollcommand=scrollbar.set)
        
        self.separate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.separate_tree.bind('<<TreeviewSelect>>', self._on_separate_select)
        
        # Populate separate list
        self._populate_separate_list()
        
        # Update status
        self.status_label.config(text="Separate Selection - Choose players who should not play together")
    
    def _show_results_screen(self, combinations):
        """Show the team generation results screen"""
        self.current_screen = "results"
        self._clear_content()
        
        # Header
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Team Generation Results", style='Subtitle.TLabel').pack(side=tk.LEFT)
        
        # Back button
        back_btn = ttk.Button(header_frame, text="← Back to Main", command=self._show_main_screen)
        back_btn.pack(side=tk.RIGHT)
        
        # Export button
        export_btn = ttk.Button(header_frame, text="Export Results", command=self._export_results, style='Secondary.TButton')
        export_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Results display
        results_frame = ttk.Frame(self.content_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget for results
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, font=('Consolas', 10))
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display results
        self._display_results(combinations)
        
        # Update status
        self.status_label.config(text=f"Results - {len(combinations)} team combinations generated")
    
    def _populate_player_list(self):
        """Populate the player list"""
        # Clear existing items
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        
        # Get all players
        players = self.player_registry.get_all_players()
        
        # Add players to treeview
        for player in sorted(players, key=lambda p: p.player_id):
            positions_str = ", ".join(pos.value for pos in player.positions)
            self.player_tree.insert('', 'end', 
                                   values=(player.player_id, player.name, positions_str,
                                          f"{player.stats.level:.1f}", 
                                          f"{player.stats.stamina:.1f}", 
                                          f"{player.stats.speed:.1f}"))
    
    def _populate_selection_list(self):
        """Populate the player selection list"""
        # Clear existing items
        for item in self.selection_tree.get_children():
            self.selection_tree.delete(item)
        
        # Get all players
        players = self.player_registry.get_all_players()
        
        # Add players to treeview
        for player in sorted(players, key=lambda p: p.player_id):
            positions_str = ", ".join(pos.value for pos in player.positions)
            self.selection_tree.insert('', 'end', 
                                      values=(player.player_id, player.name, positions_str,
                                             f"{player.stats.level:.1f}", 
                                             f"{player.stats.stamina:.1f}", 
                                             f"{player.stats.speed:.1f}"))
    
    def _populate_together_list(self):
        """Populate the together selection list"""
        # Clear existing items
        for item in self.together_tree.get_children():
            self.together_tree.delete(item)
        
        # Get selected players
        players = [self.player_registry.get_player(pid) for pid in self.selected_players]
        players = [p for p in players if p is not None]
        
        # Add players to treeview
        for player in sorted(players, key=lambda p: p.player_id):
            positions_str = ", ".join(pos.value for pos in player.positions)
            self.together_tree.insert('', 'end', 
                                     values=(player.player_id, player.name, positions_str,
                                            f"{player.stats.level:.1f}", 
                                            f"{player.stats.stamina:.1f}", 
                                            f"{player.stats.speed:.1f}"))
    
    def _populate_separate_list(self):
        """Populate the separate selection list"""
        # Clear existing items
        for item in self.separate_tree.get_children():
            self.separate_tree.delete(item)
        
        # Get selected players
        players = [self.player_registry.get_player(pid) for pid in self.selected_players]
        players = [p for p in players if p is not None]
        
        # Add players to treeview
        for player in sorted(players, key=lambda p: p.player_id):
            positions_str = ", ".join(pos.value for pos in player.positions)
            self.separate_tree.insert('', 'end', 
                                     values=(player.player_id, player.name, positions_str,
                                            f"{player.stats.level:.1f}", 
                                            f"{player.stats.stamina:.1f}", 
                                            f"{player.stats.speed:.1f}"))
    
    def _on_player_select(self, event):
        """Handle player selection in players screen"""
        if self.is_loading:
            return  # Don't update during loading
        
        selection = self.player_tree.selection()
        self.selected_players = set()
        
        for item in selection:
            values = self.player_tree.item(item, 'values')
            if values:
                player_id = int(values[0])
                self.selected_players.add(player_id)
        
        # Update button states based on selection
        self._update_player_buttons()
    
    def _on_player_double_click(self, event):
        """Handle double-click on player (edit)"""
        selection = self.player_tree.selection()
        if selection:
            item = selection[0]
            values = self.player_tree.item(item, 'values')
            if values:
                player_id = int(values[0])
                player = self.player_registry.get_player(player_id)
                if player:
                    self._edit_player_dialog(player)
    
    def _on_selection_change(self, event):
        """Handle player selection change in create teams screen"""
        if self.is_loading:
            return  # Don't update during loading
        
        selection = self.selection_tree.selection()
        self.selected_players = set()
        
        for item in selection:
            values = self.selection_tree.item(item, 'values')
            if values:
                player_id = int(values[0])
                self.selected_players.add(player_id)
        
        # Update selection label and continue button
        required_players = self.team_size_var.get() * 2
        selected_count = len(self.selected_players)
        
        self.selection_label.config(text=f"Select {selected_count} / {required_players} players")
        
        if selected_count >= required_players and not self.is_loading:
            self.continue_btn.config(state='normal')
        else:
            self.continue_btn.config(state='disabled')
    
    def _on_together_select(self, event):
        """Handle together selection"""
        # This would be implemented for multi-selection of players who should play together
        pass
    
    def _on_separate_select(self, event):
        """Handle separate selection"""
        # This would be implemented for multi-selection of players who should not play together
        pass
    
    def _add_player(self):
        """Add a new player"""
        if self.is_loading:
            return
        
        dialog = PlayerDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            def add_operation():
                # Add player to registry
                player_id = self.player_registry.add_player(dialog.result)
                
                # Save to file
                players = self.player_registry.get_all_players()
                self.data_manager.save_players(players)
                
                # Refresh UI
                self._populate_player_list()
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Player '{dialog.result.name}' added successfully!"))
            
            self._run_with_loading(add_operation, "Adding player...", "Player added successfully")
    
    def _edit_player(self):
        """Edit selected player"""
        if self.is_loading:
            return
        
        if len(self.selected_players) != 1:
            messagebox.showwarning("Warning", "Please select exactly one player to edit")
            return
        
        player_id = list(self.selected_players)[0]
        player = self.player_registry.get_player(player_id)
        
        if player:
            self._edit_player_dialog(player)
        else:
            messagebox.showerror("Error", f"Player with ID {player_id} not found")
    
    def _edit_player_dialog(self, player: Player):
        """Open edit dialog for a player"""
        dialog = PlayerDialog(self.root, player)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            def update_operation():
                # Player was updated in the dialog
                # Save to file
                players = self.player_registry.get_all_players()
                self.data_manager.save_players(players)
                
                # Refresh UI
                self._populate_player_list()
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Player '{player.name}' updated successfully!"))
            
            self._run_with_loading(update_operation, "Updating player...", "Player updated successfully")
    
    def _delete_player(self):
        """Delete selected players"""
        if self.is_loading:
            return
        
        if not self.selected_players:
            messagebox.showwarning("Warning", "Please select players to delete")
            return
        
        # Confirm deletion
        player_names = []
        for player_id in self.selected_players:
            player = self.player_registry.get_player(player_id)
            if player:
                player_names.append(player.name)
        
        if len(player_names) == 1:
            message = f"Are you sure you want to delete player '{player_names[0]}'?"
        else:
            message = f"Are you sure you want to delete {len(player_names)} players?\n\n" + "\n".join(player_names)
        
        if not messagebox.askyesno("Confirm Deletion", message):
            return
        
        def delete_operation():
            # Delete players
            deleted_count = 0
            for player_id in self.selected_players:
                if self.player_registry.remove_player(player_id):
                    deleted_count += 1
            
            # Save to file
            players = self.player_registry.get_all_players()
            self.data_manager.save_players(players)
            
            # Clear selection and refresh UI
            self.selected_players = set()
            self._populate_player_list()
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Deleted {deleted_count} player(s) successfully!"))
        
        self._run_with_loading(delete_operation, "Deleting players...", "Players deleted successfully")
    
    def _refresh_players(self):
        """Refresh player list"""
        if self.is_loading:
            return
        
        def refresh_operation():
            # Reload players from file
            players = self.data_manager.load_players()
            
            # Clear registry and reload
            self.player_registry.clear()
            for player in players:
                self.player_registry.add_player(player)
            
            # Refresh UI
            self._populate_player_list()
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", "Player list refreshed successfully!"))
        
        self._run_with_loading(refresh_operation, "Refreshing players...", "Players refreshed successfully")
    
    def _generate_teams(self):
        """Generate balanced teams"""
        if self.is_loading:
            return
        
        # Get team size
        team_size = self.team_size_var.get()
        required_players = team_size * 2
        
        if len(self.selected_players) < required_players:
            messagebox.showwarning("Warning", f"Please select at least {required_players} players")
            return
        
        def generate_operation():
            # Generate teams
            combinations = self.team_balancer.generate_balanced_teams(list(self.selected_players))
            
            if combinations:
                # Show results
                self.root.after(0, lambda: self._show_results_screen(combinations))
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No valid team combinations found with the given constraints."))
        
        self._run_with_loading(generate_operation, "Generating teams...", "Teams generated successfully")
    
    def _display_results(self, combinations):
        """Display team generation results"""
        result_text = "Generated Teams:\n" + "="*50 + "\n\n"
        
        for i, combination in enumerate(combinations[:3], 1):  # Show top 3
            result_text += f"Option {i}\n"
            result_text += f"Team 1:\n"
            
            for j, player in enumerate(combination.team1, 1):
                positions_str = ", ".join(pos.value for pos in player.positions)
                result_text += f"{j}. {player.name} ({positions_str})\n"
            
            result_text += f"\nTeam 2:\n"
            
            for j, player in enumerate(combination.team2, 1):
                positions_str = ", ".join(pos.value for pos in player.positions)
                result_text += f"{j}. {player.name} ({positions_str})\n"
            
            result_text += "\n" + "="*50 + "\n\n"
        
        self.results_text.insert(1.0, result_text)
    
    def _export_results(self):
        """Export results to file"""
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")

def main():
    """Main function"""
    root = tk.Tk()
    app = ModernTeamBalancerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()