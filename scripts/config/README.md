# Configuration Scripts

This folder contains scripts for managing application configuration and setup.

## Scripts

### `update_dynamic_config.py`
Analyzes Excel files and automatically updates configuration files based on their structure.

**Features:**
- Scans Excel files in `data/excel_files/validex/` and `data/excel_files/requirements/`
- Analyzes column structures and data types
- Updates `config/validex_config.json` and `config/sakura_config.json`
- Generates `config/dynamic_columns_summary.json`

### `create_sample_requirements.py`
Creates sample requirements Excel file for testing the Sakura app.

**Features:**
- Creates `data/excel_files/requirements/sample_requirements.xlsx`
- Includes realistic sample data
- Uses proper column structure for Sakura app

## Usage

These scripts are typically called by the main `validex_manager.py` script:

```bash
# Update configuration based on Excel files
python scripts/main/validex_manager.py config

# Create sample requirements file
python scripts/main/validex_manager.py sample
```

## Direct Usage

You can also run these scripts directly:

```bash
# Update dynamic configuration
python scripts/config/update_dynamic_config.py

# Create sample requirements
python scripts/config/create_sample_requirements.py
```
