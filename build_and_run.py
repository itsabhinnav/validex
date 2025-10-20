#!/usr/bin/env python3
"""
Validex Build and Run Script
============================

This script builds the Angular frontend and runs the Flask backend server.
It handles both development and production modes.

Usage:
    python build_and_run.py [--dev] [--prod] [--help]

Options:
    --dev     Run in development mode (default)
    --prod    Run in production mode
    --help    Show this help message

Examples:
    python build_and_run.py              # Development mode
    python build_and_run.py --dev        # Development mode (explicit)
    python build_and_run.py --prod       # Production mode
"""

import os
import sys
import subprocess
import argparse
import time
import signal
import threading
from pathlib import Path

class ValidexBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend' / 'testpoc-frontend'
        self.angular_dist = self.frontend_dir / 'dist' / 'validex-frontend'
        self.processes = []
        
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
        
    def print_step(self, step, message):
        """Print a formatted step"""
        print(f"\n[{step}] {message}")
        print("-" * 40)
        
    def run_command(self, command, cwd=None, shell=True, check=True):
        """Run a command and return the result"""
        try:
            print(f"Running: {command}")
            if cwd:
                print(f"Working directory: {cwd}")
            
            result = subprocess.run(
                command, 
                cwd=cwd, 
                shell=shell, 
                check=check,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
                
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
    
    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.print_step("1", "Checking Prerequisites")
        
        # Check Node.js
        try:
            result = self.run_command("node --version", check=False)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
            else:
                raise RuntimeError("Node.js not found. Please install Node.js.")
        except Exception as e:
            raise RuntimeError(f"Node.js check failed: {e}")
        
        # Check Angular CLI
        try:
            result = self.run_command("ng version", cwd=self.frontend_dir, check=False)
            if result.returncode == 0:
                print("✓ Angular CLI: Available")
            else:
                print("⚠️  Angular CLI not found. Installing...")
                self.run_command("npm install -g @angular/cli")
        except Exception as e:
            print(f"⚠️  Angular CLI installation failed: {e}")
            print("Please install Angular CLI manually: npm install -g @angular/cli")
        
        # Check Python
        try:
            result = self.run_command("python --version", check=False)
            if result.returncode == 0:
                print(f"✅ Python: {result.stdout.strip()}")
            else:
                raise RuntimeError("Python not found. Please install Python.")
        except Exception as e:
            raise RuntimeError(f"Python check failed: {e}")
        
        # Check if backend directory exists
        if not self.backend_dir.exists():
            raise RuntimeError(f"Backend directory not found: {self.backend_dir}")
        
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            raise RuntimeError(f"Frontend directory not found: {self.frontend_dir}")
        
        print("✓ All prerequisites met!")
    
    def install_frontend_dependencies(self):
        """Install Angular frontend dependencies"""
        self.print_step("2", "Installing Frontend Dependencies")
        
        if not (self.frontend_dir / 'node_modules').exists():
            print("Installing npm packages...")
            self.run_command("npm install", cwd=self.frontend_dir)
        else:
            print("✓ Node modules already installed")
    
    def build_angular_frontend(self, production=False):
        """Build the Angular frontend"""
        self.print_step("3", "Building Angular Frontend")
        
        if production:
            print("Building for production...")
            self.run_command("ng build --configuration production", cwd=self.frontend_dir)
        else:
            print("Building for development...")
            self.run_command("ng build", cwd=self.frontend_dir)
        
        if not self.angular_dist.exists():
            raise RuntimeError("Angular build failed - dist directory not found")
        
        print(f"✓ Angular frontend built successfully!")
        print(f"   Build output: {self.angular_dist}")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.print_step("4", "Installing Python Dependencies")
        
        try:
            self.run_command("pip install -r requirements.txt", cwd=self.backend_dir)
            print("✓ Python dependencies installed successfully")
        except Exception as e:
            print(f"⚠️  Failed to install Python dependencies: {e}")
            print("Please install manually: pip install -r backend/requirements.txt")
    
    def setup_flask_app(self):
        """Setup Flask app configuration"""
        self.print_step("5", "Setting up Flask Application")
        
        # The Flask app is already configured in backend/app.py
        # Just verify it exists
        flask_app_path = self.backend_dir / 'app.py'
        if flask_app_path.exists():
            print(f"✓ Flask app already configured: {flask_app_path}")
        else:
            raise RuntimeError(f"Flask app not found: {flask_app_path}")
    
    def run_flask_server(self):
        """Run the Flask server"""
        self.print_step("6", "Starting Flask Server")
        
        try:
            print("Starting Flask server on http://localhost:8000")
            print("Press Ctrl+C to stop the server")
            
            # Run Flask app
            self.run_command("python app.py", cwd=self.backend_dir, check=False)
            
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Flask server error: {e}")
            raise
    
    def build_and_run(self, production=False):
        """Main build and run process"""
        try:
            self.print_header("Validex Build and Run")
            
            # Step 1: Check prerequisites
            self.check_prerequisites()
            
            # Step 2: Install frontend dependencies
            self.install_frontend_dependencies()
            
            # Step 3: Build Angular frontend
            self.build_angular_frontend(production)
            
            # Step 4: Install Python dependencies
            self.install_python_dependencies()
            
            # Step 5: Setup Flask app
            self.setup_flask_app()
            
            # Step 6: Run Flask server
            self.run_flask_server()
            
        except Exception as e:
            print(f"\n✗ Build failed: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Build Angular frontend and run Flask backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dev', 
        action='store_true', 
        help='Run in development mode (default)'
    )
    
    parser.add_argument(
        '--prod', 
        action='store_true', 
        help='Run in production mode'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    production = args.prod
    if not args.dev and not args.prod:
        production = False  # Default to development
    
    # Run the builder
    builder = ValidexBuilder()
    builder.build_and_run(production=production)

if __name__ == '__main__':
    main()
