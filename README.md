# Team Balancer Pro

A modern, robust football team balancing system with advanced features for creating balanced teams based on player statistics and constraints.

## 🚀 Features

### Core Functionality
- **Multi-stat Balancing**: Considers level, stamina, and speed for optimal team balance
- **Position Management**: Support for multiple positions per player
- **Constraint System**: Must-be-together and must-be-separate player constraints
- **Diversity Filtering**: Ensures variety in team combinations
- **Real-time Validation**: Comprehensive data validation and error handling

### Advanced Features
- **Modern UI**: Clean, responsive interface with filtering and export capabilities
- **Data Persistence**: JSON-based player data storage with backup functionality
- **Configuration Management**: Flexible configuration system with file-based settings
- **Comprehensive Testing**: Full test suite with unit and integration tests
- **Logging**: Detailed logging for debugging and monitoring

## 🏗️ Architecture

### Core Components

#### 1. **Player Model** (`team_balancer.py`)
```python
@dataclass
class Player:
    name: str
    positions: List[Position]
    stats: PlayerStats
    player_id: Optional[int] = None
```

- **Type Safety**: Full type hints and validation
- **Flexible Positions**: Support for multiple positions per player
- **Stat Validation**: Ensures stats are within valid ranges (1.0-5.0)

#### 2. **Player Registry** (`team_balancer.py`)
```python
class PlayerRegistry:
    def add_player(self, player: Player) -> int
    def get_player(self, player_id: int) -> Optional[Player]
    def get_players_by_ids(self, player_ids: List[int]) -> List[Player]
```

- **Automatic ID Management**: Handles player ID assignment and uniqueness
- **Efficient Lookups**: Fast player retrieval by ID or name
- **Error Handling**: Comprehensive validation and error reporting

#### 3. **Team Balancer** (`team_balancer.py`)
```python
class TeamBalancer:
    def generate_balanced_teams(self, player_ids: List[int]) -> List[TeamCombination]
```

- **Multi-stat Algorithm**: Balances teams across all statistics
- **Constraint Processing**: Handles complex player grouping rules
- **Performance Optimized**: Efficient combination generation and filtering

#### 4. **Configuration Management** (`config.py`)
```python
@dataclass
class AppConfig:
    team_size: int = 6
    top_n_teams: int = 3
    diversity_threshold: float = 3.0
    stat_weights: Dict[str, float] = field(default_factory=lambda: {
        "level": 1.0, "stamina": 1.0, "speed": 1.0
    })
```

- **Flexible Settings**: Easy configuration of all system parameters
- **File Persistence**: Save/load configuration from JSON files
- **Validation**: Automatic validation of configuration values

#### 5. **Data Management** (`data_manager.py`)
```python
class DataManager:
    def save_players(self, players: List[Player]) -> None
    def load_players(self) -> List[Player]
    def export_players_csv(self, output_file: Path) -> None
    def validate_player_data(self, players: List[Player]) -> List[str]
```

- **Multiple Formats**: Support for JSON and CSV import/export
- **Data Validation**: Comprehensive validation of player data
- **Backup System**: Automatic backup creation and restoration

#### 6. **Modern UI** (`team_balancer_ui.py`)
```python
class ModernTeamBalancerUI:
    def _show_main_screen(self)
    def _show_players_screen(self)
    def _show_create_teams_screen(self)
    def _show_results_screen(self)
```

- **Multi-Screen Workflow**: Guided step-by-step team creation
- **Player Management**: Full CRUD operations with multi-selection

#### 7. **Streamlit Web UI** (`team_balancer_streamlit.py`)
```python
class StreamlitTeamBalancerUI:
    def run(self)
    def _show_main_page(self)
    def _show_players_page(self)
    def _show_create_teams_page(self)
```

- **Web-Based Interface**: Modern, responsive web application
- **Rich Visualizations**: Interactive charts and data tables
- **Cross-Platform**: Works on any device with a browser
- **No Widget Issues**: Eliminates Tkinter reference problems
- **Team Configuration**: Configurable team sizes (3-12 players)
- **Constraint Support**: Together/separate player rules
- **Bias-Free Results**: Clean team display without statistics
- **Export Capabilities**: Save results to files

## 📊 Data Model

### Player Structure
```json
{
  "Id": 1,
  "Name": "Player Name",
  "Position": ["DF", "MF"],
  "Stats": {
    "level": 3.5,
    "stamina": 3.2,
    "speed": 2.8
  }
}
```

### Position Enum
```python
class Position(Enum):
    GK = "GK"   # Goalkeeper
    DF = "DF"   # Defender
    MF = "MF"   # Midfielder
    FW = "FW"   # Forward
    LW = "LW"   # Left Winger
    RW = "RW"   # Right Winger
    CM = "CM"   # Center Midfielder
    CB = "CB"   # Center Back
    LB = "LB"   # Left Back
    RB = "RB"   # Right Back
```

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- tkinter (usually included with Python)

### Quick Start
```bash
# Run the modern UI
python team_balancer_ui.py

# Run the command-line version
python team_balancer.py

# Run tests
python test_team_balancer_new.py
```

### Configuration
1. **Basic Settings**: Edit `config.py` or use the UI
2. **Player Data**: Add players via UI or edit `data/players.json`
3. **Constraints**: Configure must-be-together/separate rules in config

### Example Usage
```python
from team_balancer import Player, PlayerStats, Position, TeamBalancer, TeamBalancerConfig, PlayerRegistry

# Create players
stats = PlayerStats(level=3.5, stamina=3.2, speed=2.8)
player = Player(name="John Doe", positions=[Position.DF, Position.MF], stats=stats)

# Setup balancer
registry = PlayerRegistry()
registry.add_player(player)
config = TeamBalancerConfig(team_size=6, top_n_teams=3)
balancer = TeamBalancer(config, registry)

# Generate teams
player_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
combinations = balancer.generate_balanced_teams(player_ids)
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Data Validation**: Player and configuration validation
- **Error Handling**: Exception and edge case testing

### Running Tests
```bash
# Run all tests
python -m unittest test_team_balancer_new.py -v

# Run specific test class
python -m unittest test_team_balancer_new.TestPlayerModel -v

# Run with coverage (if coverage.py is installed)
coverage run -m unittest test_team_balancer_new.py
coverage report
```

## 🔧 Configuration Options

### Team Settings
- `team_size`: Number of players per team (default: 6)
- `top_n_teams`: Number of best combinations to return (default: 3)
- `diversity_threshold`: Maximum player overlap between combinations (default: 3.0)

### Stat Weights
```python
stat_weights = {
    "level": 1.0,    # Weight for level difference
    "stamina": 1.0,  # Weight for stamina difference
    "speed": 1.0     # Weight for speed difference
}
```

### Constraints
```python
must_be_on_different_teams = [[15, 23]]  # Players who must be on different teams
must_be_on_same_teams = [[1, 2, 3]]      # Players who must be on the same team
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see requirements.txt)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`

### Running the Application

#### Option 1: Modern Web Interface (Recommended)
```bash
# Run the Streamlit web app
python run_streamlit.py
# or
streamlit run team_balancer_streamlit.py
```
Then open your browser to `http://localhost:8501`

#### Option 2: Traditional Desktop Interface
```bash
# Run the Tkinter desktop app
python team_balancer_ui.py
```

### Why Streamlit?
The Streamlit version provides:
- ✅ **No widget errors** - Eliminates Tkinter reference issues
- ✅ **Web-based interface** - Accessible from any device
- ✅ **Better performance** - Faster and more responsive
- ✅ **Rich visualizations** - Charts and data tables
- ✅ **Cross-platform** - Works on any operating system

## 📁 File Structure
```
footbal/
├── team_balancer.py              # Core balancing logic and models
├── team_balancer_ui.py           # Traditional Tkinter GUI interface
├── team_balancer_streamlit.py    # Modern Streamlit web interface
├── run_streamlit.py              # Streamlit launcher script
├── config.py                     # Configuration management
├── data_manager.py               # Data persistence and validation
├── player_manager.py             # Command-line player management
├── initialize_data.py            # Data initialization script
├── test_team_balancer_new.py     # Comprehensive test suite
├── requirements.txt              # Python dependencies
├── DOCUMENTATION.md              # Main documentation index
├── README.md                     # This file
├── data/                         # Data directory
│   ├── players.json              # Player data
│   └── config.json               # Configuration
└── logs/                         # Log files
    └── team_balancer.log         # Application logs
```

## 📚 Documentation

For comprehensive documentation, see **[DOCUMENTATION.md](DOCUMENTATION.md)** which serves as the main index for all documentation files.

## 🚀 Modern Architecture

### Key Features
1. **ID Management**: Automatic, conflict-free ID assignment
2. **Type Safety**: Full type hints and validation
3. **Error Handling**: Comprehensive error handling and recovery
4. **Performance**: Optimized algorithms and caching
5. **Maintainability**: Clean separation of concerns
6. **Extensibility**: Modular design for easy feature addition

### Data Management
- JSON-based player data storage with validation
- Configuration management with automatic persistence
- Backup and restore functionality
- Real-time data synchronization

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Data Validation**: Check player stats are within 1.0-5.0 range
3. **Configuration**: Verify configuration file format
4. **Permissions**: Ensure write access to data and log directories

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for all classes and methods
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆕 Recent Changes

### Version 2.0 (Current)
- Complete architectural refactoring
- Modern UI with filtering and export
- Comprehensive data management
- Full test coverage
- Configuration management system
- Performance optimizations

### Version 1.0 (Previous)
- Basic team balancing functionality
- Simple command-line interface
- JSON-based data storage
- Enhanced error handling

For detailed change history, see `CHANGES_SUMMARY.md`. 