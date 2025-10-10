# 🚀 Validex - Test Case Management System

A comprehensive Flask-based web application for managing and executing test cases with enterprise-grade features including role-based access, scalable architecture, and modern UI.

## 📄 License

This project is open source and available under the MIT License.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)

## 🎯 Overview

Validex is a **portable team distribution** test case management platform designed for enterprise use. It provides a complete solution for managing test cases stored in test files, executing tests, and generating comprehensive reports. The system is optimized for **client-side distribution** to team members rather than server hosting.

### Key Highlights
- **Portable Distribution**: Self-contained package for team distribution
- **Localhost-Only Security**: Binds only to 127.0.0.1 for maximum security
- **Team Collaboration**: Artifactory integration for shared test files
- **No Server Required**: Each team member runs their own instance
- **Offline Capable**: Works without network dependencies
- **Enterprise-Ready**: Scalable architecture supporting 400,000+ test cases

## 🚀 Quick Start

### For Team Distribution
```bash
# Build team distribution package
python scripts/build_team_distribution.py

# Distribute to team members
# Team members run: pip install -r requirements.txt
# Team members run: python scripts/configure_team.py
# Team members run: ./start_team.sh
```

### For Development
```bash
# Clone and setup
git clone <repository-url>
cd testPoc
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py
```

## 📚 Documentation

**Complete documentation is available in the `docs/` folder:**

- **[docs/README.md](docs/README.md)** - Comprehensive documentation including:
  - Architecture overview
  - Team distribution guide
  - Security guide
  - Build guide
  - License analysis
- **[docs/PWA_GUIDE.md](docs/PWA_GUIDE.md)** - Progressive Web App features
- **[docs/TEXT_CONFIGURATION.md](docs/TEXT_CONFIGURATION.md)** - Text configuration
- **[docs/LICENSING.md](docs/LICENSING.md)** - Licensing information

## ✨ Features

### 🎭 Role-Based Access Control
- **Administrator Role**: 
  - Manage test files and test cases
  - Configure system settings
  - View comprehensive reports
  - Manage user permissions
- **Tester Role**:
  - Execute test cases
  - Filter and search test scenarios
  - Submit test results
  - View execution reports

### 📊 Advanced Test Management
- **Test File Support**: Load test cases from test files with flexible column mapping
- **Dynamic Filtering**: Advanced filtering by feature, status, priority, app, test type
- **Search Functionality**: Full-text search across test cases
- **Test Execution**: Execute individual test cases with result tracking
- **Reporting**: Comprehensive test execution reports and analytics

### 🏗️ Scalable Architecture
- **Database-Backed**: SQLite with FTS5 for fast searching
- **Pagination**: Efficient handling of large datasets
- **Caching**: Smart caching for improved performance
- **Remote Sync**: JFrog Artifactory integration for remote file management
- **Incremental Processing**: Only process changed files

### 🎨 Modern User Interface
- **Responsive Design**: Mobile-friendly interface
- ** Styling**: Modern gradients and animations
- **Interactive Elements**: Hover effects and smooth transitions
- **Accessibility**: WCAG compliant design
- **Dark/Light Themes**: User preference support

## 🏛️ Architecture

### Project Structure
```
test_case_management/
├── run.py                          # Application entry point
├── requirements.txt                # Dependencies
├── README.md                       # This documentation
├── data/
│   ├── test_cases.db               # SQLite database
│   ├── excel_files/                # Test files
│   ├── reports/                    # Generated reports
│   └── cache/                      # Cache directory
├── config/                         # Configuration management
│   ├── __init__.py
│   ├── settings.py                 # Main configuration
│   ├── database.py                 # Database configuration
│   └── column_config.json          # Column definitions
├── app/                           # Application layer
│   ├── __init__.py                 # Flask app factory
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── test_case.py
│   │   ├── file_metadata.py
│   │   └── sync_status.py
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   ├── database_service.py
│   │   ├── file_service.py
│   │   ├── sync_service.py
│   │   └── column_service.py
│   ├── api/                        # HTTP endpoints
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── auth.py
│   │   └── admin.py
│   ├── utils/                      # Utility functions
│   │   └── __init__.py
│   ├── templates/                  # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── test_cases.html
│   │   ├── admin.html
│   │   └── setup.html
│   └── static/                     # Static assets
│       ├── css/
│       │   └── main.css
│       └── js/
│           └── main.js
├── core/                          # Core functionality
│   ├── __init__.py
│   ├── database/                  # Database operations
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── sync/                      # Sync operations
│   │   ├── __init__.py
│   │   └── remote_sync.py
│   └── storage/                   # File management
│       └── __init__.py
├── tests/                         # Test suite
│   └── __init__.py
├── scripts/                       # Utility scripts
│   ├── __init__.py
│   └── migrate_to_new_structure.py
├── docs/                          # Documentation
├── data/                          # Data storage
│   ├── excel_files/               # Test files
│   │   └── validex/               # Test data
│   ├── reports/                   # Generated reports
│   └── cache/                     # Cache directory
└── venv/                          # Virtual environment
```

### Architecture Components

#### 1. **Application Layer (`app/`)**
- **Models**: Data models for test cases, file metadata, and sync status
- **Services**: Business logic for database, file, sync, and column management
- **API**: HTTP endpoints for routes, authentication, and admin functions
- **Templates**: HTML templates with Jinja2 templating
- **Static Assets**: CSS and JavaScript files

#### 2. **Core Layer (`core/`)**
- **Database Manager**: SQLite operations with FTS5 support
- **Sync Manager**: Remote file synchronization
- **Storage Manager**: File management and caching

#### 3. **Configuration Layer (`config/`)**
- **Settings**: Application configuration
- **Database Config**: Database connection settings
- **Column Config**: Extensible column definitions

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- Git (for cloning)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd testPoc
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests**
   ```bash
   python -m pytest tests/
   ```

3. **Run with debug mode**
   ```bash
   export FLASK_ENV=development
   python run.py
   ```

## 📖 Usage

### Getting Started

1. **Access the Application**: Navigate to `http://localhost:8000`
2. **Select Role**: Choose between Administrator or Tester role
3. **Load Test Cases**: Upload test files or use existing ones
4. **Execute Tests**: Run test cases and record results
5. **View Reports**: Analyze test execution results

### Test File Format

The application supports flexible test file formats with the following standard columns:

| Column | Description | Required |
|--------|-------------|----------|
| `TC ID` | Unique test case identifier | ✅ |
| `Summary` | Test case description | ✅ |
| `Feature` | Feature or module being tested | ✅ |
| `Priority` | Test priority (High, Medium, Low) | ✅ |
| `Status` | Current status (Pending, Passed, Failed) | ✅ |
| `Screen ID` | Screen or page identifier | ❌ |
| `Test Type` | Type of test (FMEA, Sanity, Smoke, etc.) | ❌ |
| `Expected Behavior` | Detailed expected behavior | ❌ |
| `Procedure` | Test execution steps | ❌ |
| `Preconditions` | Prerequisites for test execution | ❌ |

### Role-Specific Features

#### Administrator Features
- **File Management**: Upload, edit, and delete test files
- **Test Case Management**: Add, edit, and delete test cases
- **System Configuration**: Configure column mappings and settings
- **User Management**: Manage user roles and permissions
- **Reports**: View comprehensive system reports

#### Tester Features
- **Test Execution**: Execute individual test cases
- **Result Submission**: Submit test results with comments
- **Filtering**: Advanced filtering and search capabilities
- **Reports**: View personal execution reports
- **Dashboard**: Overview of assigned test cases

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `FLASK_DEBUG` | Debug mode | True |
| `DATABASE_URL` | Database connection URL | sqlite:///data/test_cases.db |
| `UPLOAD_FOLDER` | Test files directory | data/excel_files |
| `REPORTS_FOLDER` | Reports directory | data/reports |

### Configuration Files

#### `config/settings.py`
Main application configuration with environment-specific settings.

#### `config/validex_config.json`
Single source of truth for all application configuration including:
- Application settings (name, version, debug mode)
- Database configuration (path, backup settings)
- File system settings (directories, file size limits)
- JFrog Artifactory integration
- Network security settings
- UI and text configuration
- Column mappings and export settings

### Remote Sync Configuration

For JFrog Artifactory integration:

```json
{
  "jfrog": {
    "base_url": "https://your-artifactory.com",
    "repository": "test-repo",
    "root_path": "test-cases",
    "access_token": "your-access-token",
    "enabled": true
  }
}
```

## 🔌 API Documentation

### Main Routes

| Route | Method | Description | Role |
|-------|--------|-------------|------|
| `/` | GET | Landing page | Public |
| `/role-selection` | GET | Role selection page | Public |
| `/select_role` | POST | Select user role | Public |
| `/dashboard` | GET | Main dashboard | Authenticated |
| `/test_cases` | GET | Test cases listing | Tester |
| `/execute_test/<id>` | GET | Test execution page | Tester |
| `/submit_test_result` | POST | Submit test result | Tester |
| `/admin` | GET | Admin panel | Admin |
| `/reports` | GET | Execution reports | Tester |
| `/logout` | GET | Logout user | Authenticated |

### API Endpoints

#### Test Cases API
```http
GET /api/test_cases?page=1&limit=50&filter=status:passed
POST /api/test_cases
PUT /api/test_cases/<id>
DELETE /api/test_cases/<id>
```

#### Reports API
```http
GET /api/reports
GET /api/reports/<id>
POST /api/reports
```

#### Sync API
```http
POST /api/sync/initial
POST /api/sync/incremental
GET /api/sync/status
```

## 🚀 Scalability & Performance

### Performance Optimizations

#### Database Optimizations
- **FTS5 Full-Text Search**: Fast text searching across test cases
- **Indexing**: Optimized indexes for common queries
- **Pagination**: Efficient handling of large datasets
- **Connection Pooling**: Optimized database connections

#### Caching Strategy
- **File Metadata Caching**: Cache file modification times and hashes
- **Query Result Caching**: Cache frequently accessed data
- **Static Asset Caching**: Browser caching for CSS/JS files

#### Scalability Features
- **Hybrid Storage**: Local and remote file synchronization
- **Incremental Sync**: Only process changed files
- **Background Processing**: Async file processing
- **Load Balancing**: Support for multiple instances

### Performance Benchmarks

| Metric | Value |
|--------|-------|
| Test Cases Supported | 400,000+ |
| Files Supported | 10,000+ |
| Search Response Time | < 100ms |
| Page Load Time | < 2s |
| Memory Usage | < 500MB |
| Database Size | < 1GB |

## 🛠️ Development

### Development Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd testPoc
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run in development mode**
   ```bash
   export FLASK_ENV=development
   python run.py
   ```

3. **Run tests**
   ```bash
   python -m pytest tests/
   ```

### Code Structure

#### Services Layer
- **DatabaseService**: Database operations and queries
- **FileService**: File management and test file processing
- **SyncService**: Remote synchronization
- **ColumnService**: Column configuration management

#### Models Layer
- **TestCase**: Test case data model
- **FileMetadata**: File metadata tracking
- **SyncStatus**: Synchronization status

#### API Layer
- **Routes**: Main application routes
- **Auth**: Authentication and authorization
- **Admin**: Administrative functions

### Adding New Features

1. **Create Service**: Add business logic in `app/services/`
2. **Create Model**: Add data models in `app/models/`
3. **Create Route**: Add API endpoints in `app/api/`
4. **Create Template**: Add HTML templates in `app/templates/`
5. **Add Tests**: Create tests in `tests/`

### Code Style

- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type annotations
- **Docstrings**: Document all functions and classes
- **Error Handling**: Comprehensive error handling
- **Logging**: Use proper logging levels

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Not Starting
```bash
# Check Python version
python --version

# Check virtual environment
which python  # or where python on Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Issues
```bash
# Reset database
rm data/test_cases.db
python run.py  # Will recreate database
```

#### 3. Test Files Not Loading
- Check file format and column names
- Ensure files are in `data/excel_files/` directory
- Verify file permissions

#### 4. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### 5. Static Files Not Loading
- Check `app/static/` directory exists
- Verify Flask static file configuration
- Clear browser cache

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
python run.py
```

### Logging

Application logs are available in:
- Console output (development)
- `logs/app.log` (production)

## 🤝 Contributing

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests for new functionality**
5. **Run the test suite**
   ```bash
   python -m pytest tests/
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Create a Pull Request**

### Development Guidelines

- **Code Quality**: Follow PEP 8 and use type hints
- **Testing**: Write tests for new features
- **Documentation**: Update documentation for changes
- **Performance**: Consider performance implications
- **Security**: Follow security best practices

### Pull Request Process

1. **Update README.md** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update documentation**
5. **Request review** from maintainers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review this README and inline documentation
2. **Search Issues**: Look for similar issues in the repository
3. **Create Issue**: Submit a detailed issue report
4. **Community**: Join discussions in the repository

### Issue Reporting

When reporting issues, please include:
- **Environment**: OS, Python version, dependencies
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Logs**: Relevant error messages and logs

### Feature Requests

For feature requests, please include:
- **Use Case**: Why this feature is needed
- **Proposed Solution**: How you envision it working
- **Alternatives**: Other solutions you've considered
- **Additional Context**: Any other relevant information

---

## 🎉 Acknowledgments

- **Flask**: Web framework
- **Bootstrap**: UI framework
- **SQLite**: Database engine
- **Pandas**: Test file processing
- **Font Awesome**: Icons

---

**Validex -  Test Case Management Made Simple** 🚀

*Built with ❤️ for the testing community*