# 🚀 Validex Production Deployment Guide

This guide provides multiple deployment options for the Validex Test Case Management System in production environments.

## 📋 Quick Start Options

### Option 1: Automated Setup (Recommended)
```bash
# Linux/macOS
chmod +x scripts/production_setup.sh
./scripts/production_setup.sh

# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1
```

### Option 2: Docker Deployment
```bash
# Using Docker Compose
docker-compose up -d

# Using Docker only
docker build -t validex .
docker run -d -p 8000:8000 --name validex-app validex
```

### Option 3: Manual Setup
Follow the detailed steps in [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

## 🛠️ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Stable internet connection

### Recommended for Production
- **OS**: Linux (Ubuntu 22.04 LTS)
- **RAM**: 8GB or more
- **Storage**: 50GB+ SSD
- **CPU**: 2+ cores
- **Network**: High-speed internet

## 🚀 Deployment Methods

### 1. Linux Production Deployment

#### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv git nginx sqlite3 curl wget -y
```

#### Automated Setup
```bash
# Clone repository
git clone <your-repo-url>
cd testPoc

# Run automated setup
chmod +x scripts/production_setup.sh
./scripts/production_setup.sh
```

#### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/excel_files data/reports data/cache logs

# Initialize database
python -c "from app import create_app; from app.services.database_service import DatabaseService; app = create_app('production'); db_service = DatabaseService(); db_service.initialize()"

# Start application
python run.py
```

### 2. Windows Production Deployment

#### Prerequisites
- Python 3.8+ from [python.org](https://python.org)
- Git from [git-scm.com](https://git-scm.com)
- PowerShell 5.1+

#### Automated Setup
```powershell
# Clone repository
git clone <your-repo-url>
cd testPoc

# Run automated setup
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1
```

#### Manual Setup
```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir data\excel_files, data\reports, data\cache, logs

# Initialize database
python -c "from app import create_app; from app.services.database_service import DatabaseService; app = create_app('production'); db_service = DatabaseService(); db_service.initialize()"

# Start application
python run.py
```

### 3. Docker Deployment

#### Using Docker Compose (Recommended)
```bash
# Create environment file
cp env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f validex
```

#### Using Docker Only
```bash
# Build image
docker build -t validex .

# Run container
docker run -d \
  --name validex-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  validex
```

### 4. Cloud Deployment

#### AWS EC2
```bash
# Launch Ubuntu 22.04 LTS instance
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow Linux deployment steps
```

#### Google Cloud Platform
```bash
# Create VM instance
gcloud compute instances create validex-server \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh validex-server --zone=us-central1-a

# Follow Linux deployment steps
```

#### Azure
```bash
# Create VM using Azure CLI
az vm create \
  --resource-group myResourceGroup \
  --name validex-vm \
  --image Ubuntu2204 \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH into instance
ssh azureuser@your-vm-ip

# Follow Linux deployment steps
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key

# Database
DATABASE_URL=sqlite:///data/test_cases.db

# File Storage
UPLOAD_FOLDER=data/excel_files
REPORTS_FOLDER=data/reports

# Server
HOST=0.0.0.0
PORT=8000

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# JFrog Integration (Optional)
JFROG_BASE_URL=https://your-artifactory.com
JFROG_REPOSITORY=your-repo
JFROG_ACCESS_TOKEN=your-token
JFROG_ENABLED=False
```

### Database Configuration
The application uses SQLite by default. For production with high concurrency, consider PostgreSQL:

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb validex
sudo -u postgres createuser validex_user

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://validex_user:password@localhost/validex
```

### Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Using Let's Encrypt (Free)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Using custom certificates
# Place certificates in /etc/nginx/ssl/
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# iptables (CentOS/RHEL)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### Application Security
```python
# In config/settings.py
class ProductionConfig:
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload limits
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "Application is healthy"
else
    echo "Application is down"
    systemctl restart validex
fi
EOF

chmod +x health_check.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/health_check.sh") | crontab -
```

### Backup Script
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# Backup database
cp data/test_cases.db "$BACKUP_DIR/test_cases_$DATE.db"

# Backup files
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" data/excel_files/

# Clean old backups
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

### Log Management
```bash
# Setup log rotation
sudo nano /etc/logrotate.d/validex
```

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

## 🚨 Troubleshooting

### Common Issues

1. **Application won't start**
```bash
# Check logs
journalctl -u validex -f
tail -f logs/app.log

# Check permissions
ls -la data/
sudo chown -R www-data:www-data data/
```

2. **Database issues**
```bash
# Check database integrity
sqlite3 data/test_cases.db "PRAGMA integrity_check;"

# Rebuild database
rm data/test_cases.db
python -c "from app import create_app; from app.services.database_service import DatabaseService; app = create_app('production'); db_service = DatabaseService(); db_service.initialize()"
```

3. **File upload issues**
```bash
# Check file permissions
chmod 755 data/excel_files/
chown -R www-data:www-data data/
```

4. **Port already in use**
```bash
# Find process using port 8000
lsof -i :8000
netstat -tulpn | grep :8000

# Kill process
sudo kill -9 <PID>
```

### Performance Optimization

1. **Database Optimization**
```sql
-- Optimize SQLite
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
```

2. **Application Optimization**
```python
# Enable caching
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Database connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
```

3. **Web Server Optimization**
```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript;

# Enable caching
location /static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📞 Support

### Getting Help
1. Check application logs: `logs/app.log`
2. Check system logs: `journalctl -u validex`
3. Monitor system resources: `htop`, `df -h`
4. Test database connectivity: `sqlite3 data/test_cases.db ".tables"`

### Useful Commands
```bash
# Service management
sudo systemctl status validex
sudo systemctl restart validex
sudo systemctl stop validex
sudo systemctl start validex

# Log viewing
sudo journalctl -u validex -f
tail -f logs/app.log

# Database management
sqlite3 data/test_cases.db
.tables
.schema
.quit

# File management
ls -la data/
du -sh data/
```

---

**🎉 Your Validex Test Case Management System is now ready for production use!**

For additional support and advanced configuration options, refer to the detailed [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) guide.
