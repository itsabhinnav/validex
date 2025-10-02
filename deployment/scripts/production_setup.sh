#!/bin/bash
# Validex Production Setup Script
# This script automates the production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
APP_NAME="validex"
APP_USER="www-data"
APP_DIR="/opt/validex"
DOMAIN=""
EMAIL=""
SECRET_KEY=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        print_status "Please run as a regular user with sudo privileges"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if running on supported OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check available memory
    if [[ "$OS" == "linux" ]]; then
        MEMORY_GB=$(free -g | awk 'NR==2{print $2}')
        if [[ $MEMORY_GB -lt 4 ]]; then
            print_warning "Less than 4GB RAM available. Performance may be affected."
        fi
    fi
    
    print_success "System requirements check completed"
}

# Function to install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        # Update package list
        sudo apt update
        
        # Install required packages
        sudo apt install -y python3 python3-pip python3-venv git nginx \
            sqlite3 curl wget unzip software-properties-common \
            libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev \
            build-essential python3-dev
        
        # Install Node.js for PM2 (optional)
        if ! command -v node &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt install -y nodejs
        fi
        
    elif [[ "$OS" == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install required packages
        brew install python3 git nginx sqlite3 curl wget node
    fi
    
    print_success "System dependencies installed"
}

# Function to create application user
create_app_user() {
    print_status "Creating application user..."
    
    if [[ "$OS" == "linux" ]]; then
        if ! id "$APP_USER" &>/dev/null; then
            sudo useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
            print_success "Created user: $APP_USER"
        else
            print_status "User $APP_USER already exists"
        fi
    fi
}

# Function to setup application directory
setup_app_directory() {
    print_status "Setting up application directory..."
    
    # Create application directory
    sudo mkdir -p "$APP_DIR"
    sudo chown $USER:$APP_USER "$APP_DIR"
    
    # Create necessary subdirectories
    mkdir -p "$APP_DIR/data/excel_files"
    mkdir -p "$APP_DIR/data/reports"
    mkdir -p "$APP_DIR/data/cache"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/backups"
    
    # Set proper permissions
    chmod 755 "$APP_DIR"
    chmod 755 "$APP_DIR/data"
    chmod 755 "$APP_DIR/logs"
    
    print_success "Application directory created: $APP_DIR"
}

# Function to clone and setup application
setup_application() {
    print_status "Setting up application..."
    
    # Navigate to application directory
    cd "$APP_DIR"
    
    # Clone repository (replace with actual repository URL)
    if [[ ! -d "app" ]]; then
        print_status "Please clone your repository to $APP_DIR"
        print_status "Example: git clone <your-repo-url> ."
        read -p "Press Enter after cloning the repository..."
    fi
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_success "Application setup completed"
}

# Function to configure environment
configure_environment() {
    print_status "Configuring environment..."
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Create .env file
    cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$SECRET_KEY
DATABASE_URL=sqlite:///data/test_cases.db
UPLOAD_FOLDER=data/excel_files
REPORTS_FOLDER=data/reports
HOST=0.0.0.0
PORT=8000
EOF
    
    # Create production configuration
    cat > config/production.py << EOF
import os

class ProductionConfig:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/test_cases.db')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'data/excel_files')
    REPORTS_FOLDER = os.environ.get('REPORTS_FOLDER', 'data/reports')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
EOF
    
    print_success "Environment configured"
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Initialize database
    python3 -c "
from app import create_app
from app.services.database_service import DatabaseService

app = create_app('production')
with app.app_context():
    db_service = DatabaseService()
    db_service.initialize()
    print('Database initialized successfully')
"
    
    print_success "Database initialized"
}

# Function to setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/validex.service > /dev/null << EOF
[Unit]
Description=Validex Test Case Management System
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable validex
    
    print_success "Systemd service configured"
}

# Function to setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/validex > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # File upload size
    client_max_body_size 100M;
    
    # Static files
    location /static {
        alias $APP_DIR/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/validex /etc/nginx/sites-enabled/
    
    # Remove default site if it exists
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    sudo nginx -t
    
    print_success "Nginx configured"
}

# Function to setup SSL certificate
setup_ssl() {
    if [[ -n "$DOMAIN" && -n "$EMAIL" ]]; then
        print_status "Setting up SSL certificate..."
        
        # Install Certbot
        sudo apt install -y certbot python3-certbot-nginx
        
        # Obtain SSL certificate
        sudo certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
        
        print_success "SSL certificate configured"
    else
        print_warning "Skipping SSL setup (domain or email not provided)"
    fi
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80
    sudo ufw allow 443
    
    print_success "Firewall configured"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create health check script
    cat > "$APP_DIR/monitor.sh" << 'EOF'
#!/bin/bash
APP_URL="http://localhost:8000"
LOG_FILE="/opt/validex/logs/health.log"

if curl -f -s "$APP_URL" > /dev/null; then
    echo "$(date): Application is healthy" >> "$LOG_FILE"
else
    echo "$(date): Application is down - restarting" >> "$LOG_FILE"
    systemctl restart validex
fi
EOF
    
    chmod +x "$APP_DIR/monitor.sh"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -
    
    print_success "Monitoring configured"
}

# Function to setup backups
setup_backups() {
    print_status "Setting up backups..."
    
    # Create backup script
    cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/validex/backups"
APP_DIR="/opt/validex"
DATE=$(date +%Y%m%d_%H%M%S)

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
    
    chmod +x "$APP_DIR/backup.sh"
    
    # Schedule daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -
    
    print_success "Backups configured"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start application
    sudo systemctl start validex
    sudo systemctl status validex --no-pager
    
    # Start Nginx
    sudo systemctl restart nginx
    sudo systemctl status nginx --no-pager
    
    print_success "Services started"
}

# Function to display final information
display_final_info() {
    print_success "Validex production setup completed!"
    echo
    print_status "Application Information:"
    echo "  - Application Directory: $APP_DIR"
    echo "  - Service Name: validex"
    echo "  - Port: 8000"
    echo "  - User: $APP_USER"
    echo
    print_status "Useful Commands:"
    echo "  - Check status: sudo systemctl status validex"
    echo "  - View logs: sudo journalctl -u validex -f"
    echo "  - Restart app: sudo systemctl restart validex"
    echo "  - Check Nginx: sudo systemctl status nginx"
    echo
    if [[ -n "$DOMAIN" ]]; then
        print_status "Access your application at: http://$DOMAIN"
    else
        print_status "Access your application at: http://localhost"
    fi
    echo
    print_warning "Don't forget to:"
    echo "  1. Configure your domain DNS"
    echo "  2. Update firewall rules if needed"
    echo "  3. Test the application thoroughly"
    echo "  4. Set up monitoring and alerting"
}

# Main execution
main() {
    print_status "Starting Validex production setup..."
    
    # Get user input
    read -p "Enter your domain name (or press Enter to skip): " DOMAIN
    read -p "Enter your email for SSL certificate (or press Enter to skip): " EMAIL
    
    # Execute setup steps
    check_root
    check_requirements
    install_dependencies
    create_app_user
    setup_app_directory
    setup_application
    configure_environment
    initialize_database
    setup_systemd_service
    setup_nginx
    setup_ssl
    setup_firewall
    setup_monitoring
    setup_backups
    start_services
    display_final_info
}

# Run main function
main "$@"
