# Validex Manager - Unified Script

A comprehensive command-line tool that combines all Validex operations into a single, easy-to-use script.

## [QUICK] Quick Start

### Windows
```batch
# Show help
scripts\validex.bat help

# Run dynamic configuration analysis
scripts\validex.bat config

# Check application status
scripts\validex.bat status

# Create sample requirements
scripts\validex.bat sample

# Build all distributions
scripts\validex.bat build --all
```

### Unix/Linux/macOS
```bash
# Make executable (first time only)
chmod +x scripts/validex.sh

# Show help
./scripts/validex.sh help

# Run dynamic configuration analysis
./scripts/validex.sh config

# Check application status
./scripts/validex.sh status

# Create sample requirements
./scripts/validex.sh sample

# Build all distributions
./scripts/validex.sh build --all
```

### Direct Python
```bash
# Show help
python scripts/validex.py help

# Run dynamic configuration analysis
python scripts/validex.py config

# Check application status
python scripts/validex.py status

# Create sample requirements
python scripts/validex.py sample

# Build all distributions
python scripts/validex.py build --all
```

## [COMMANDS] Commands

### `config` - Dynamic Configuration Analysis
Analyzes Excel files in Validex directories and updates configuration files automatically.

```bash
python scripts/validex.py config
```

**What it does:**
- Scans `data/excel_files/validex/` for test case files
- Scans `data/excel_files/requirements/` for requirements files
- Analyzes column structures and data types
- Updates `config/validex_config.json`
- Generates `config/dynamic_columns_summary.json`

### `sample` - Create Sample Test Cases
Creates sample test case Excel files for testing the Validex app.

```bash
python scripts/validex.py sample
```

**What it does:**
- Creates `data/excel_files/validex/sample_test_cases.xlsx`
- Includes sample data with realistic test cases
- Uses proper column structure for Validex app

### `build` - Build Distributions
Builds various distribution packages for deployment.

```bash
# Build all distributions
python scripts/validex.py build --all

# Build portable distribution only
python scripts/validex.py build --portable

# Build executable distribution only
python scripts/validex.py build --executable

# Build desktop app distribution only
python scripts/validex.py build --desktop
```

**What it does:**
- **Portable**: Creates a self-contained ZIP package
- **Executable**: Creates a standalone executable file
- **Desktop**: Creates a desktop application package

### `status` - Application Status
Shows the current status of all applications and their Excel files.

```bash
python scripts/validex.py status
```

**What it shows:**
- Number of Excel files found for each app
- List of all Excel files
- Directory status for each app

### `clean` - Clean Build Directory
Removes all build artifacts and temporary files.

```bash
python scripts/validex.py clean
```

**What it does:**
- Removes the entire `build/` directory
- Cleans up temporary files
- Frees up disk space

## [FEATURES] Features

### [OK] **Unified Interface**
- Single script for all operations
- Consistent command-line interface
- Cross-platform support (Windows, Linux, macOS)

### [OK] **Dynamic Configuration**
- Automatic Excel file analysis
- Column structure detection
- Data type inference
- Configuration file updates

### [OK] **Multiple Build Types**
- Portable distributions
- Executable files
- Desktop applications
- All-in-one builds

### [OK] **Comprehensive Logging**
- Timestamped log messages
- File logging to `logs/validex_manager.log`
- Console output with status indicators
- Error handling and reporting

### [OK] **Sample Data Generation**
- Pre-configured sample files
- Realistic test data
- Proper column structures

## [STRUCTURE] File Structure

```
scripts/
├── validex.py             # Main script launcher
├── validex.bat            # Windows batch file
├── validex.sh             # Unix/Linux shell script
├── README.md              # This documentation
├── build/                 # Build-related scripts
│   ├── README.md
│   ├── build_all_distributions.py
│   ├── build_desktop_app.py
│   ├── build_executable.py
│   ├── build_portable_final.py
│   ├── build.bat
│   └── build.sh
├── config/                # Configuration scripts
│   ├── README.md
│   ├── create_sample_requirements.py
│   └── update_dynamic_config.py
├── main/                  # Main entry point scripts
│   ├── README.md
│   ├── validex_manager.py
│   ├── validex.bat
│   └── validex.sh
└── utils/                 # Utility scripts (future)
    └── README.md
```

## [USAGE] Use Cases

### **Development Workflow**
1. **Setup**: `python scripts/validex.py sample`
2. **Configure**: `python scripts/validex.py config`
3. **Test**: `python scripts/validex.py status`
4. **Build**: `python scripts/validex.py build --all`

### **Production Deployment**
1. **Analyze**: `python scripts/validex.py config`
2. **Build**: `python scripts/validex.py build --portable`
3. **Deploy**: Distribute the generated ZIP file

### **Maintenance**
1. **Check Status**: `python scripts/validex.py status`
2. **Update Config**: `python scripts/validex.py config`
3. **Clean Builds**: `python scripts/validex.py clean`

## [TROUBLESHOOT] Troubleshooting

### **Common Issues**

**Permission Denied (Unix/Linux)**
```bash
chmod +x scripts/validex.sh
```

**Python Not Found**
```bash
# Use python3 instead
python3 scripts/validex_manager.py help
```

**Import Errors**
```bash
# Make sure you're in the project root
cd /path/to/testPoc
python scripts/validex.py help
```

**Build Failures**
```bash
# Clean and retry
python scripts/validex.py clean
python scripts/validex.py build --portable
```

### **Log Files**
- **Console Output**: Real-time status messages
- **Log File**: `logs/validex_manager.log` (detailed logging)
- **Build Logs**: Individual build scripts may create their own logs

## [ADVANCED] Advanced Usage

### **Custom Build Options**
```bash
# Build specific distribution types
python scripts/validex.py build --portable --executable

# Clean before building
python scripts/validex.py clean && python scripts/validex.py build --all
```

### **Automation Scripts**
```bash
#!/bin/bash
# deploy.sh - Automated deployment script
python scripts/validex.py config
python scripts/validex.py build --portable
echo "Deployment package ready!"
```

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Build Validex
  run: |
    python scripts/validex.py config
    python scripts/validex.py build --all
```

## [EXAMPLES] Output Examples

### **Status Command Output**
```
[01:20:49] Checking application status...
[01:20:49] Application Status:
[01:20:49]   [OK] VALIDEX: 18 Excel files
[01:20:49]     - app1_fmea_tests.xlsx
[01:20:49]     - app1_sanity_tests.xlsx
[01:20:49]     - app1_smoke_tests.xlsx
[01:20:49]   [OK] SAKURA: 1 Excel files
[01:20:49]     - sample_requirements.xlsx
```

### **Config Command Output**
```
[01:21:00] Starting dynamic configuration analysis...
[01:21:01] Dynamic configuration analysis completed successfully!
[01:21:01] VALIDEX: 18 files, 8 columns
[01:21:01]   Required: 8 columns
[01:21:01]   Optional: 0 columns
[01:21:01] SAKURA: 1 files, 13 columns
[01:21:01]   Required: 13 columns
[01:21:01]   Optional: 0 columns
```

## [BENEFITS] Benefits

- **[UNIFIED] Unified Workflow**: One script for all operations
- **⚡ Fast Execution**: Optimized for speed and efficiency
- **[SECURE] Error Handling**: Comprehensive error checking and reporting
- **📝 Detailed Logging**: Full audit trail of all operations
- **[CROSS-PLATFORM] Cross-Platform**: Works on Windows, Linux, and macOS
- **[MAINTENANCE] Easy Maintenance**: Simple command-line interface
- **📦 All-in-One**: Replaces multiple individual scripts

---

**Need Help?** Run `python scripts/validex.py help` for detailed usage information.
