#!/bin/bash
# Validex Quick Start Script
# For development and testing purposes

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then
    print_warning "Python 3.8+ recommended. Found: $PYTHON_VERSION"
fi

print_status "Setting up Validex for development..."

# Create virtual environment
if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_status "Creating directories..."
mkdir -p data/excel_files
mkdir -p data/reports
mkdir -p data/cache
mkdir -p logs

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_status "Creating environment file..."
    cp env.example .env
    print_warning "Please update .env file with your configuration"
fi

# Initialize database
print_status "Initializing database..."
python -c "
from app import create_app
from app.services.database_service import DatabaseService

app = create_app('development')
with app.app_context():
    db_service = DatabaseService()
    db_service.initialize()
    print('Database initialized successfully')
"

print_success "Validex setup completed!"
echo
print_status "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the application: python run.py"
echo "  3. Open browser: http://localhost:8000"
echo
print_status "For production deployment, use:"
echo "  ./scripts/production_setup.sh"
