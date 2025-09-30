# Test Case Management System

A Flask-based web application for managing and executing test cases, similar to Qase or Xray test management tools. This application provides role-based access for administrators and testers to manage test cases stored in Excel files.

## Features

- **Role-based Access**: Separate interfaces for Administrators and Testers
- **Excel File Management**: Load and manage test cases from Excel files
- **Test Execution**: Execute individual test cases and record results
- **Reporting**: View test execution reports and statistics
- **Filtering**: Filter test cases by file, status, feature, etc.
- **Modern UI**: Bootstrap-based responsive interface

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd test-trace
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

4. **Create sample Excel files (optional)**
   ```bash
   python create_sample_excel.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

## Usage

### Role Selection
- **Administrator**: Can manage Excel files, view all reports, and configure system settings
- **Tester**: Can execute test cases, filter and search test scenarios, and submit results

### Excel File Format
The application expects Excel files with the following columns:
- `Test Case ID`: Unique identifier for the test case
- `Test Case Title`: Descriptive title of the test case
- `Feature`: Feature or module being tested
- `Priority`: Test priority (High, Medium, Low)
- `Status`: Current status (Pending, Passed, Failed, etc.)
- `Preconditions`: Prerequisites for test execution
- `Given`: Initial context or setup
- `When`: Action to be performed
- `Then`: Expected outcome
- `Expected Behavior`: Detailed expected behavior
- `Remarks`: Additional notes or comments

### File Structure
```
test-trace/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── create_sample_excel.py         # Script to create sample Excel files
├── README.md                      # This file
├── venv/                          # Virtual environment (created after setup)
├── excel_files/                   # Directory for Excel test case files
│   ├── ecommerce_test_cases.xlsx
│   ├── banking_test_cases.xlsx
│   └── mobile_test_cases.xlsx
├── templates/                     # HTML templates
│   ├── base.html
│   ├── role_selection.html
│   ├── dashboard.html
│   ├── test_cases.html
│   ├── execute_test.html
│   ├── admin.html
│   └── reports.html
└── reports/                       # Generated test execution reports
    └── test_execution_report.jsonl
```

## Features Overview

### Dashboard
- Overview of loaded Excel files and test case counts
- Quick access to main functionalities
- Role-specific navigation

### Test Cases Management
- Browse all test cases with filtering options
- Search by file, status, or feature
- Execute individual test cases

### Test Execution
- Detailed test case information display
- Result submission (Passed, Failed, Blocked, Skipped)
- Execution time tracking
- Comments and remarks

### Admin Panel
- Excel file management
- System statistics
- Configuration options (future feature)

### Reports
- Test execution history
- Pass/fail statistics
- Export functionality (future feature)

## Future Enhancements

### CLI Tool
- Download Excel files from JFrog Artifactory
- Batch processing of test cases
- Database migration from Excel files
- Automated test case validation

### Database Integration
- Migration from Excel to database
- Advanced querying and reporting
- Data persistence and backup

### Additional Features
- User authentication and authorization
- Advanced filtering and search
- Test case versioning
- Integration with CI/CD pipelines
- Automated test execution
- Advanced reporting and analytics

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to 'development' for debug mode
- `FLASK_DEBUG`: Enable/disable debug mode

### File Locations
- Excel files: `excel_files/` directory
- Reports: `reports/` directory
- Templates: `templates/` directory

## API Endpoints

- `/` - Role selection page
- `/dashboard` - Main dashboard
- `/test_cases` - Test cases listing with filters
- `/execute_test/<test_id>` - Test execution page
- `/admin` - Admin panel (admin role only)
- `/reports` - Execution reports
- `/logout` - Logout and clear session

## Troubleshooting

### Common Issues

1. **Excel files not loading**
   - Ensure files are in the `excel_files/` directory
   - Check file format and column names
   - Verify file permissions

2. **Application not starting**
   - Check Python version (3.8+ required)
   - Ensure virtual environment is activated
   - Install all dependencies from requirements.txt

3. **Templates not found**
   - Ensure `templates/` directory exists
   - Check template file names and syntax

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Create an issue in the repository

---

**Note**: This is a demo application for test case management. For production use, implement proper authentication, database integration, and security measures.


