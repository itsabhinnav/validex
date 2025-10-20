# Validex Build and Run Script for PowerShell
# ===========================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Validex Build and Run Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Backend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "frontend\testpoc-frontend")) {
    Write-Host "ERROR: Frontend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1] Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Angular CLI
Set-Location "frontend\testpoc-frontend"
try {
    $ngVersion = ng version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Angular CLI: Available" -ForegroundColor Green
    } else {
        throw "Angular CLI not found"
    }
} catch {
    Write-Host "⚠️  Angular CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g @angular/cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Angular CLI" -ForegroundColor Red
        Write-Host "Please install manually: npm install -g @angular/cli" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "[2] Installing Frontend Dependencies..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install npm packages" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✅ Node modules already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3] Building Angular Frontend..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Building for development..." -ForegroundColor Cyan
ng build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Angular build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "dist\testpoc-frontend")) {
    Write-Host "ERROR: Angular build output not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Angular frontend built successfully!" -ForegroundColor Green

Set-Location "..\.."

Write-Host ""
Write-Host "[4] Setting up Flask Application..." -ForegroundColor Yellow
Write-Host ""

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
Set-Location "backend"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ".."
Write-Host "✅ Flask app configured" -ForegroundColor Green

Write-Host ""
Write-Host "[5] Starting Flask Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Starting Validex Server" -ForegroundColor Cyan
Write-Host "📡 API Endpoints: http://localhost:8000/api/*" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Flask Templates: http://localhost:8000/test-cases" -ForegroundColor Cyan
Write-Host "🔄 Split View: http://localhost:8000/test-cases-split" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "backend"
python app.py

Write-Host ""
Write-Host "🛑 Server stopped" -ForegroundColor Red
Read-Host "Press Enter to exit"
