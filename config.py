#!/usr/bin/env python3
"""
Configuration management for Team Balancer
"""

from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration"""
    
    # Team settings
    team_size: int = 6
    top_n_teams: int = 3
    diversity_threshold: float = 3.0
    
    # Player constraints
    must_be_on_different_teams: List[List[int]] = field(default_factory=lambda: [[15, 23]])
    must_be_on_same_teams: List[List[int]] = field(default_factory=list)
    
    # Stat weights for balance calculation
    stat_weights: Dict[str, float] = field(default_factory=lambda: {
        "level": 1.0, 
        "stamina": 1.0, 
        "speed": 1.0
    })
    
    # File paths
    data_dir: Path = Path("data")
    players_file: Path = Path("data/players.json")
    config_file: Path = Path("data/config.json")
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("logs/team_balancer.log")
    
    def __post_init__(self):
        """Ensure directories exist"""
        self.data_dir.mkdir(exist_ok=True)
        self.log_file.parent.mkdir(exist_ok=True)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "team_size": self.team_size,
            "top_n_teams": self.top_n_teams,
            "diversity_threshold": self.diversity_threshold,
            "must_be_on_different_teams": self.must_be_on_different_teams,
            "must_be_on_same_teams": self.must_be_on_same_teams,
            "stat_weights": self.stat_weights,
            "log_level": self.log_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AppConfig":
        """Create from dictionary"""
        return cls(**data)
    
    def save(self) -> None:
        """Save configuration to file"""
        import json
        with open(self.config_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from file"""
        import json
        if cls().config_file.exists():
            with open(cls().config_file, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        return cls()

# Default configuration
DEFAULT_CONFIG = AppConfig()

# Football positions
POSITIONS_ALLOWED = ["GK", "DF", "MF", "FW", "LW", "RW", "CM", "CB", "LB", "RB"]

# Stat validation ranges
STAT_MIN_VALUE = 1.0
STAT_MAX_VALUE = 5.0 