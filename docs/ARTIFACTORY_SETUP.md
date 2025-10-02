# 🔧 JFrog Artifactory Setup Guide

Since you have your Excel files and database in JFrog Artifactory, follow these steps to configure and sync your Validex application.

## 📋 Prerequisites

✅ **Completed:**
- Cloned the repository
- Installed dependencies (`pip install -r requirements.txt`)

## 🚀 Quick Setup

### **Option 1: Automated Setup (Recommended)**

```bash
# Run the automated setup script
python scripts/setup_artifactory.py
```

The script will guide you through:
1. Entering your Artifactory URL
2. Repository name
3. Project path
4. Access token
5. Automatic file download and configuration

### **Option 2: Manual Configuration**

#### **Step 1: Update Configuration**

Edit `config/validex_config.json`:

```json
{
  "jfrog": {
    "base_url": "https://your-company.jfrog.io/artifactory",
    "repository": "your-repository-name",
    "root_path": "your-project-path",
    "access_token": "your-access-token",
    "enabled": true
  },
  "app": {
    "excel_files_dir": "data/excel_files",
    "reports_dir": "data/reports",
    "auto_refresh_interval": 30
  }
}
```

#### **Step 2: Create Environment File**

Create `.env` file in the root directory:

```bash
# Validex Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///data/test_cases.db
UPLOAD_FOLDER=data/excel_files
REPORTS_FOLDER=data/reports
HOST=0.0.0.0
PORT=8000

# JFrog Artifactory Integration
JFROG_ENABLED=true
```

#### **Step 3: Download Files from Artifactory**

You can either:

**A. Use the sync service (if implemented):**
```python
from app.services.sync_service import SyncService
from app.services.database_service import DatabaseService
from app.services.file_service import FileService

# Initialize services
db_service = DatabaseService()
file_service = FileService()
sync_service = SyncService(db_service, file_service)

# Configure and start sync
result = sync_service.configure_remote_sync(
    remote_url="your-artifactory-url",
    api_token="your-access-token",
    strategy="complete"
)
```

**B. Manual download:**
- Download your Excel files to `data/excel_files/`
- Download your database file to `data/test_cases.db`

#### **Step 4: Initialize Database**

```bash
python -c "
from app import create_app
from app.services.database_service import DatabaseService

app = create_app('production')
with app.app_context():
    db_service = DatabaseService()
    db_service.initialize()
    print('Database initialized successfully')
"
```

#### **Step 5: Start Application**

```bash
python run.py
```

## 🔍 Verification

### **Check File Structure**
```bash
# Verify Excel files are in place
ls -la data/excel_files/

# Verify database exists
ls -la data/test_cases.db

# Check configuration
cat config/validex_config.json
```

### **Test Application**
1. Open browser: `http://localhost:8000`
2. Navigate to dashboard
3. Check if test cases are loaded
4. Verify file counts and statistics

## 🔄 Sync Strategies

The application supports different sync strategies:

### **Minimal Sync**
- Downloads only metadata
- Fastest setup
- Good for initial configuration

### **Selective Sync**
- Downloads specific apps or test types
- Balanced approach
- Good for focused testing

### **Complete Sync**
- Downloads all files
- Full functionality
- Recommended for production

## 🛠️ Troubleshooting

### **Common Issues**

1. **Connection Failed**
   - Verify Artifactory URL
   - Check access token permissions
   - Ensure repository exists

2. **Files Not Found**
   - Check root path configuration
   - Verify file names and extensions
   - Ensure files are in correct repository

3. **Database Issues**
   - Check database file permissions
   - Verify SQLite file integrity
   - Reinitialize if needed

4. **Application Won't Start**
   - Check environment variables
   - Verify all dependencies installed
   - Check logs for errors

### **Debug Commands**

```bash
# Test Artifactory connection
python -c "
import requests
import json
with open('config/validex_config.json') as f:
    config = json.load(f)
jfrog = config['jfrog']
headers = {'Authorization': f'Bearer {jfrog[\"access_token\"]}'}
response = requests.get(f'{jfrog[\"base_url\"]}/api/storage/{jfrog[\"repository\"]}', headers=headers)
print(f'Status: {response.status_code}')
"

# Check database
sqlite3 data/test_cases.db ".tables"

# Check file permissions
ls -la data/
```

## 📊 Expected Results

After successful setup, you should see:

1. **Application running** on `http://localhost:8000`
2. **Test cases loaded** from your Excel files
3. **Database populated** with test case data
4. **Dashboard showing** statistics and file counts
5. **All features working** (search, filter, execute, reports)

## 🔄 Ongoing Sync

For ongoing synchronization:

1. **Automatic Sync**: Configured in `validex_config.json`
2. **Manual Sync**: Use the sync service API
3. **Scheduled Sync**: Set up cron jobs or scheduled tasks

## 📞 Support

If you encounter issues:

1. Check the logs: `logs/app.log`
2. Verify configuration: `config/validex_config.json`
3. Test connection: Use debug commands above
4. Review file permissions and paths

---

**🎉 Your Validex application should now be connected to JFrog Artifactory and ready to use!**
