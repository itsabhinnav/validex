# 🚀 Validex Production Deployment Guide

This guide provides comprehensive instructions for deploying the Validex Test Case Management System in a production environment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 10GB free space
- **Network**: Stable internet connection for JFrog integration (optional)

### Software Dependencies
- Python 3.8+
- Git
- Virtual Environment (venv or conda)
- Web server (Nginx/Apache) for production
- Process manager (systemd, PM2, or supervisor)

## 🛠️ Step-by-Step Production Setup

### 1. System Preparation

#### Windows Setup:
```powershell
# Install Python (if not already installed)
# Download from https://python.org/downloads/
# Ensure "Add Python to PATH" is checked

# Install Git
# Download from https://git-scm.com/download/win

# Verify installations
python --version
git --version
```

#### Linux Setup (Ubuntu/Debian):
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git nginx -y

# Install additional dependencies for Excel processing
sudo apt install libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev -y
```

#### macOS Setup:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python3 git nginx
```

### 2. Clone and Setup Application

```bash
# Clone the repository
git clone <your-repository-url>
cd testPoc

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

#### Create Production Environment File:
```bash
# Create .env file for production settings
cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=sqlite:///data/test_cases.db
UPLOAD_FOLDER=data/excel_files
REPORTS_FOLDER=data/reports
HOST=0.0.0.0
PORT=8000
EOF
```

#### Update Configuration Files:

**config/settings.py** - Production Configuration:
```python
class ProductionConfig:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prod-secret-key-change-this')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/test_cases.db')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'data/excel_files')
    REPORTS_FOLDER = os.environ.get('REPORTS_FOLDER', 'data/reports')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
```

### 4. Database and Directory Setup

```bash
# Create necessary directories
mkdir -p data/excel_files
mkdir -p data/reports
mkdir -p data/cache
mkdir -p logs

# Set proper permissions (Linux/macOS)
chmod 755 data/
chmod 755 logs/

# Initialize database
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

### 5. Security Configuration

#### Generate Secure Secret Key:
```python
# Generate a secure secret key
import secrets
print(secrets.token_hex(32))
```

#### Update Security Settings:
```python
# In config/settings.py
class ProductionConfig:
    # ... existing settings ...
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
```

### 6. Web Server Configuration

#### Nginx Configuration:
```nginx
# /etc/nginx/sites-available/validex
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # File upload size
    client_max_body_size 100M;
    
    # Static files
    location /static {
        alias /path/to/validex/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### Enable Nginx Site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/validex /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 7. Process Management

#### Using systemd (Linux):

**Create service file:**
```bash
sudo nano /etc/systemd/system/validex.service
```

**Service configuration:**
```ini
[Unit]
Description=Validex Test Case Management System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/validex
Environment=PATH=/path/to/validex/venv/bin
ExecStart=/path/to/validex/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable validex
sudo systemctl start validex
sudo systemctl status validex
```

#### Using PM2 (Cross-platform):

```bash
# Install PM2 globally
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'validex',
    script: 'run.py',
    interpreter: 'venv/bin/python',
    cwd: '/path/to/validex',
    instances: 1,
    exec_mode: 'fork',
    env: {
      FLASK_ENV: 'production',
      PORT: 8000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 8. SSL Certificate (HTTPS)

#### Using Let's Encrypt (Free SSL):
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured by default)
sudo certbot renew --dry-run
```

### 9. Firewall Configuration

#### Linux (UFW):
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application port (if direct access needed)
sudo ufw allow 8000

# Check status
sudo ufw status
```

#### Windows (Windows Firewall):
```powershell
# Allow application through Windows Firewall
New-NetFirewallRule -DisplayName "Validex App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### 10. Monitoring and Logging

#### Setup Log Rotation:
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/validex
```

**Logrotate configuration:**
```
/path/to/validex/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload validex
    endscript
}
```

#### Setup Monitoring Script:
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# Validex Health Check Script

APP_URL="http://localhost:8000"
LOG_FILE="/path/to/validex/logs/health.log"

# Check if application is responding
if curl -f -s "$APP_URL" > /dev/null; then
    echo "$(date): Application is healthy" >> "$LOG_FILE"
else
    echo "$(date): Application is down - restarting" >> "$LOG_FILE"
    systemctl restart validex
fi
EOF

chmod +x monitor.sh

# Add to crontab for regular health checks
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/validex/monitor.sh") | crontab -
```

### 11. Backup Configuration

#### Database Backup Script:
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# Validex Backup Script

BACKUP_DIR="/path/to/backups"
APP_DIR="/path/to/validex"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
cp "$APP_DIR/data/test_cases.db" "$BACKUP_DIR/test_cases_$DATE.db"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" "$APP_DIR/config/"

# Backup uploaded files
tar -czf "$BACKUP_DIR/excel_files_$DATE.tar.gz" "$APP_DIR/data/excel_files/"

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "$(date): Backup completed" >> "$BACKUP_DIR/backup.log"
EOF

chmod +x backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/validex/backup.sh") | crontab -
```

### 12. Performance Optimization

#### Database Optimization:
```sql
-- Optimize SQLite database
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
```

#### Application Optimization:
```python
# In config/settings.py
class ProductionConfig:
    # ... existing settings ...
    
    # Performance settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Caching
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
```

### 13. JFrog Integration (Optional)

#### Configure JFrog Artifactory:
```bash
# Update JFrog configuration
cat > config/validex_config.json << EOF
{
  "jfrog": {
    "base_url": "https://your-artifactory.com",
    "repository": "your-repo",
    "root_path": "test-cases",
    "access_token": "your-access-token",
    "enabled": true
  },
  "app": {
    "excel_files_dir": "data/excel_files",
    "reports_dir": "data/reports",
    "auto_refresh_interval": 30
  }
}
EOF
```

### 14. Final Verification

#### Health Check Commands:
```bash
# Check application status
curl -I http://localhost:8000

# Check database
sqlite3 data/test_cases.db ".tables"

# Check logs
tail -f logs/app.log

# Check system resources
htop
df -h
```

#### Application Testing:
```bash
# Test all endpoints
curl http://localhost:8000/
curl http://localhost:8000/role-selection
curl http://localhost:8000/dashboard

# Test file upload (if applicable)
curl -X POST -F "file=@test.xlsx" http://localhost:8000/upload
```

## 🔧 Maintenance and Updates

### Regular Maintenance Tasks:

1. **Database Maintenance:**
```bash
# Optimize database monthly
sqlite3 data/test_cases.db "VACUUM;"
sqlite3 data/test_cases.db "ANALYZE;"
```

2. **Log Cleanup:**
```bash
# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

3. **Security Updates:**
```bash
# Update dependencies
pip install --upgrade -r requirements.txt
```

4. **Backup Verification:**
```bash
# Test backup restoration
sqlite3 test_restore.db < backup.sql
```

## 🚨 Troubleshooting

### Common Issues:

1. **Application won't start:**
```bash
# Check logs
journalctl -u validex -f
tail -f logs/app.log

# Check permissions
ls -la data/
chown -R www-data:www-data data/
```

2. **Database issues:**
```bash
# Check database integrity
sqlite3 data/test_cases.db "PRAGMA integrity_check;"

# Rebuild database if needed
rm data/test_cases.db
python -c "from app import create_app; from app.services.database_service import DatabaseService; app = create_app('production'); db_service = DatabaseService(); db_service.initialize()"
```

3. **File upload issues:**
```bash
# Check file permissions
chmod 755 data/excel_files/
chown -R www-data:www-data data/
```

## 📞 Support

For production support and troubleshooting:
- Check application logs: `logs/app.log`
- Check system logs: `journalctl -u validex`
- Monitor system resources: `htop`, `df -h`
- Test database connectivity: `sqlite3 data/test_cases.db ".tables"`

---

**🎉 Congratulations! Your Validex Test Case Management System is now ready for production use.**
