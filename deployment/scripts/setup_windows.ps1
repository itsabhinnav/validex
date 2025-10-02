# Validex Windows Setup Script
# PowerShell script for Windows deployment

param(
    [string]$Domain = "",
    [string]$Email = "",
    [string]$AppDir = "C:\validex"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check system requirements
function Test-Requirements {
    Write-Status "Checking system requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Python is not installed. Please install Python 3.8+ from https://python.org"
            exit 1
        }
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Python is not installed. Please install Python 3.8+ from https://python.org"
        exit 1
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Git is not installed. Please install Git from https://git-scm.com"
            exit 1
        }
        Write-Success "Git found: $gitVersion"
    }
    catch {
        Write-Error "Git is not installed. Please install Git from https://git-scm.com"
        exit 1
    }
    
    Write-Success "System requirements check completed"
}

# Install Python dependencies
function Install-Dependencies {
    Write-Status "Installing Python dependencies..."
    
    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Status "Creating virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install requirements
    if (Test-Path "requirements.txt") {
        Write-Status "Installing requirements..."
        pip install -r requirements.txt
    } else {
        Write-Error "requirements.txt not found"
        exit 1
    }
    
    Write-Success "Dependencies installed"
}

# Setup application directories
function Setup-Directories {
    Write-Status "Setting up application directories..."
    
    $directories = @(
        "data\excel_files",
        "data\reports", 
        "data\cache",
        "logs",
        "backups"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Created directory: $dir"
        }
    }
    
    Write-Success "Directories created"
}

# Configure environment
function Setup-Environment {
    Write-Status "Configuring environment..."
    
    # Generate secret key
    $secretKey = -join ((1..32) | ForEach {[char]((65..90) + (97..122) | Get-Random)})
    
    # Create .env file
    if (-not (Test-Path ".env")) {
        $envContent = @"
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$secretKey
DATABASE_URL=sqlite:///data/test_cases.db
UPLOAD_FOLDER=data/excel_files
REPORTS_FOLDER=data/reports
HOST=0.0.0.0
PORT=8000
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Environment file created"
    } else {
        Write-Status "Environment file already exists"
    }
}

# Initialize database
function Initialize-Database {
    Write-Status "Initializing database..."
    
    try {
        python -c "
from app import create_app
from app.services.database_service import DatabaseService

app = create_app('production')
with app.app_context():
    db_service = DatabaseService()
    db_service.initialize()
    print('Database initialized successfully')
"
        Write-Success "Database initialized"
    }
    catch {
        Write-Error "Failed to initialize database: $_"
        exit 1
    }
}

# Setup Windows Service
function Setup-WindowsService {
    Write-Status "Setting up Windows Service..."
    
    $serviceName = "Validex"
    $serviceDisplayName = "Validex Test Case Management System"
    $serviceDescription = "Validex Test Case Management System Service"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Status "Service already exists, stopping and removing..."
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        sc.exe delete $serviceName
    }
    
    # Create service
    $currentPath = Get-Location
    $pythonPath = "$currentPath\venv\Scripts\python.exe"
    $scriptPath = "$currentPath\run.py"
    
    sc.exe create $serviceName binPath= "$pythonPath $scriptPath" DisplayName= "$serviceDisplayName" start= auto
    sc.exe description $serviceName "$serviceDescription"
    
    Write-Success "Windows Service created"
}

# Setup Nginx (if available)
function Setup-Nginx {
    Write-Status "Setting up Nginx..."
    
    # Check if Nginx is installed
    try {
        nginx -v 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Nginx found, configuring..."
            
            $nginxConfig = @"
server {
    listen 80;
    server_name $Domain;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}
"@
            
            $nginxConfig | Out-File -FilePath "nginx.conf" -Encoding UTF8
            Write-Success "Nginx configuration created"
        }
    }
    catch {
        Write-Warning "Nginx not found, skipping configuration"
    }
}

# Setup firewall rules
function Setup-Firewall {
    Write-Status "Setting up Windows Firewall..."
    
    try {
        # Allow application through firewall
        New-NetFirewallRule -DisplayName "Validex App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
        Write-Success "Firewall rule created"
    }
    catch {
        Write-Warning "Failed to create firewall rule: $_"
    }
}

# Create monitoring script
function Setup-Monitoring {
    Write-Status "Setting up monitoring..."
    
    $monitorScript = @"
# Validex Health Check Script
`$appUrl = "http://localhost:8000"
`$logFile = "logs\health.log"

try {
    `$response = Invoke-WebRequest -Uri `$appUrl -TimeoutSec 10 -UseBasicParsing
    if (`$response.StatusCode -eq 200) {
        Add-Content -Path `$logFile -Value "`$(Get-Date): Application is healthy"
    } else {
        Add-Content -Path `$logFile -Value "`$(Get-Date): Application returned status `$(`$response.StatusCode)"
        Restart-Service -Name "Validex" -Force
    }
} catch {
    Add-Content -Path `$logFile -Value "`$(Get-Date): Application is down - restarting"
    Restart-Service -Name "Validex" -Force
}
"@
    
    $monitorScript | Out-File -FilePath "monitor.ps1" -Encoding UTF8
    Write-Success "Monitoring script created"
}

# Create backup script
function Setup-Backup {
    Write-Status "Setting up backup..."
    
    $backupScript = @"
# Validex Backup Script
`$backupDir = "backups"
`$date = Get-Date -Format "yyyyMMdd_HHmmss"

# Create backup directory
if (-not (Test-Path `$backupDir)) {
    New-Item -ItemType Directory -Path `$backupDir
}

# Backup database
if (Test-Path "data\test_cases.db") {
    Copy-Item "data\test_cases.db" "`$backupDir\test_cases_`$date.db"
}

# Backup configuration
Compress-Archive -Path "config\*" -DestinationPath "`$backupDir\config_`$date.zip" -Force

# Backup uploaded files
if (Test-Path "data\excel_files") {
    Compress-Archive -Path "data\excel_files\*" -DestinationPath "`$backupDir\excel_files_`$date.zip" -Force
}

# Clean old backups (keep last 30 days)
Get-ChildItem -Path `$backupDir -Name "*.db" | Where-Object { (Get-Item `$_).CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force
Get-ChildItem -Path `$backupDir -Name "*.zip" | Where-Object { (Get-Item `$_).CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force

Add-Content -Path "`$backupDir\backup.log" -Value "`$(Get-Date): Backup completed"
"@
    
    $backupScript | Out-File -FilePath "backup.ps1" -Encoding UTF8
    Write-Success "Backup script created"
}

# Start services
function Start-Services {
    Write-Status "Starting services..."
    
    try {
        Start-Service -Name "Validex"
        Write-Success "Validex service started"
    }
    catch {
        Write-Error "Failed to start Validex service: $_"
    }
}

# Display final information
function Show-FinalInfo {
    Write-Success "Validex Windows setup completed!"
    Write-Host ""
    Write-Status "Application Information:"
    Write-Host "  - Service Name: Validex"
    Write-Host "  - Port: 8000"
    Write-Host "  - Application Directory: $(Get-Location)"
    Write-Host ""
    Write-Status "Useful Commands:"
    Write-Host "  - Check service: Get-Service -Name Validex"
    Write-Host "  - Start service: Start-Service -Name Validex"
    Write-Host "  - Stop service: Stop-Service -Name Validex"
    Write-Host "  - View logs: Get-EventLog -LogName Application -Source Validex"
    Write-Host ""
    if ($Domain) {
        Write-Status "Access your application at: http://$Domain"
    } else {
        Write-Status "Access your application at: http://localhost:8000"
    }
    Write-Host ""
    Write-Warning "Don't forget to:"
    Write-Host "  1. Configure your domain DNS"
    Write-Host "  2. Update Windows Firewall rules if needed"
    Write-Host "  3. Test the application thoroughly"
    Write-Host "  4. Set up monitoring and alerting"
}

# Main execution
function Main {
    Write-Status "Starting Validex Windows setup..."
    
    # Get user input if not provided
    if (-not $Domain) {
        $Domain = Read-Host "Enter your domain name (or press Enter to skip)"
    }
    if (-not $Email) {
        $Email = Read-Host "Enter your email for SSL certificate (or press Enter to skip)"
    }
    
    # Execute setup steps
    Test-Requirements
    Install-Dependencies
    Setup-Directories
    Setup-Environment
    Initialize-Database
    Setup-WindowsService
    Setup-Nginx
    Setup-Firewall
    Setup-Monitoring
    Setup-Backup
    Start-Services
    Show-FinalInfo
}

# Run main function
Main
