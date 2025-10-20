# Main Scripts

This folder contains the main entry point scripts for the Validex application.

## Scripts

### `validex_manager.py`
The unified script that combines all Validex operations into a single command-line tool.

**Features:**
- Dynamic configuration analysis
- Sample data generation
- Build management
- Application status checking
- Build directory cleaning
- Comprehensive logging

### `validex.bat` / `validex.sh`
Platform-specific launcher scripts for easy access.

## Usage

### Windows
```batch
# Show help
scripts\main\validex.bat help

# Run configuration analysis
scripts\main\validex.bat config

# Build all distributions
scripts\main\validex.bat build --all
```

### Unix/Linux/macOS
```bash
# Make executable (first time only)
chmod +x scripts/main/validex.sh

# Show help
./scripts/main/validex.sh help

# Run configuration analysis
./scripts/main/validex.sh config

# Build all distributions
./scripts/main/validex.sh build --all
```

### Direct Python
```bash
# Show help
python scripts/main/validex_manager.py help

# Run configuration analysis
python scripts/main/validex_manager.py config

# Build all distributions
python scripts/main/validex_manager.py build --all
```

## Commands

- `config` - Dynamic configuration analysis
- `sample` - Create sample requirements file
- `build` - Build distributions (--all, --portable, --executable, --desktop)
- `status` - Show application status
- `clean` - Clean build directory
- `help` - Show help information
