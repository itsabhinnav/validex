#!/usr/bin/env python3
"""
Validex Development Server Runner
=================================

This script runs both Angular frontend and Flask backend simultaneously
for development purposes with improved process management and logging.

Usage:
    python run_dev.py [options]

Options:
    --frontend-port PORT    Angular dev server port (default: 4200)
    --backend-port PORT     Flask API server port (default: 8000)
    --no-frontend          Run only backend server
    --no-backend           Run only frontend server
    --install-deps         Install dependencies before starting
    --help                 Show this help message

Examples:
    python run_dev.py                           # Run both servers
    python run_dev.py --frontend-port 3000      # Custom frontend port
    python run_dev.py --no-frontend            # Backend only
    python run_dev.py --install-deps           # Install deps and run
"""

import subprocess
import sys
import time
import signal
import os
import threading
import argparse
from pathlib import Path
from datetime import datetime

class ValidexDevRunner:
    def __init__(self, frontend_port=4200, backend_port=8000, debug=False):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend' / 'testpoc-frontend'
        self.frontend_port = frontend_port
        self.backend_port = backend_port
        self.debug = debug
        self.processes = []
        self.running = True
        self.log_lock = threading.Lock()

    def log(self, message, level="INFO"):
        """Thread-safe logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self.log_lock:
            if level == "DEBUG" and not self.debug:
                return
            print(f"[{timestamp}] [{level}] {message}")

    def print_header(self):
        """Print startup header"""
        print("\n" + "="*70)
        print(" Validex Development Server Runner")
        print("="*70)
        print(f" Project Root: {self.project_root}")
        print(f" Frontend Port: {self.frontend_port}")
        print(f" Backend Port: {self.backend_port}")
        print("="*70)

    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.log("Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Node.js: {result.stdout.strip()}")
            else:
                raise RuntimeError("Node.js not found")
        except Exception as e:
            self.log(f"Node.js check failed: {e}", "ERROR")
            return False

        # Check Python
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Python: {result.stdout.strip()}")
            else:
                raise RuntimeError("Python not found")
        except Exception as e:
            self.log(f"Python check failed: {e}", "ERROR")
            return False

        # Check directories
        if not self.backend_dir.exists():
            self.log(f"Backend directory not found: {self.backend_dir}", "ERROR")
            return False

        if not self.frontend_dir.exists():
            self.log(f"Frontend directory not found: {self.frontend_dir}", "ERROR")
            return False

        self.log("All prerequisites met!", "SUCCESS")
        return True

    def install_dependencies(self):
        """Install frontend and backend dependencies"""
        self.log("Installing dependencies...")
        
        # Install frontend dependencies
        if (self.frontend_dir / 'package.json').exists():
            self.log("Installing frontend dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"], 
                    cwd=self.frontend_dir, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    self.log("Frontend dependencies installed successfully", "SUCCESS")
                else:
                    self.log(f"Frontend dependency installation failed: {result.stderr}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"Frontend dependency installation error: {e}", "ERROR")
                return False

        # Install backend dependencies
        if (self.backend_dir / 'requirements.txt').exists():
            self.log("Installing backend dependencies...")
            try:
                result = subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"], 
                    cwd=self.backend_dir, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    self.log("Backend dependencies installed successfully", "SUCCESS")
                else:
                    self.log(f"Backend dependency installation failed: {result.stderr}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"Backend dependency installation error: {e}", "ERROR")
                return False

        return True

    def start_backend_server(self):
        """Start Flask API server"""
        self.log("Starting Flask API Server...")
        try:
            # Check if app.py exists
            app_py_path = self.backend_dir / "app.py"
            if not app_py_path.exists():
                self.log(f"app.py not found at {app_py_path}", "ERROR")
                return False
            
            # Create Flask startup command
            cmd = [sys.executable, str(app_py_path)]
            
            self.log(f"Running command: {' '.join(cmd)}", "DEBUG")
            self.log(f"Working directory: {self.backend_dir}", "DEBUG")
            
            # Start Flask server
            process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(("backend", process))
            
            # Wait for server to start and check if it's still running
            time.sleep(3)
            
            if process.poll() is None:
                self.log(f"[OK] Flask API Server started on http://localhost:{self.backend_port}", "SUCCESS")
                self.log(f"   API Endpoints: http://localhost:{self.backend_port}/api/*", "INFO")
                return True
            else:
                # Get the output to see what went wrong
                stdout, stderr = process.communicate()
                self.log(f"[ERROR] Flask server failed to start", "ERROR")
                if stdout:
                    self.log(f"Flask output: {stdout}", "ERROR")
                if stderr:
                    self.log(f"Flask error: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"[ERROR] Failed to start Flask server: {e}", "ERROR")
            return False

    def start_frontend_server(self):
        """Start Angular development server"""
        self.log("Starting Angular Development Server...")
        try:
            # Check if package.json exists
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                self.log(f"package.json not found at {package_json}", "ERROR")
                return False
            
            # Check if Angular CLI is available globally
            try:
                result = subprocess.run(
                    ["ng", "version"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.log("Using global Angular CLI", "DEBUG")
                    # Use global ng command
                    cmd = [
                        "ng", "serve", 
                        "--port", str(self.frontend_port),
                        "--host", "0.0.0.0",
                        "--disable-host-check"
                    ]
                else:
                    raise FileNotFoundError("ng command not found")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.log("Angular CLI not found globally. Trying npx...", "WARN")
                # Try using npx instead
                cmd = [
                    "npx", "@angular/cli", "serve", 
                    "--port", str(self.frontend_port),
                    "--host", "0.0.0.0",
                    "--disable-host-check"
                ]
            
            self.log(f"Running command: {' '.join(cmd)}", "DEBUG")
            self.log(f"Working directory: {self.frontend_dir}", "DEBUG")
            
            process = subprocess.Popen(
                cmd,
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(("frontend", process))
            
            # Wait for server to start
            time.sleep(8)
            
            if process.poll() is None:
                self.log(f"[OK] Angular Development Server started on http://localhost:{self.frontend_port}", "SUCCESS")
                self.log("   Hot Reload: Enabled", "INFO")
                return True
            else:
                # Get the output to see what went wrong
                stdout, stderr = process.communicate()
                self.log(f"[ERROR] Angular server failed to start", "ERROR")
                if stdout:
                    self.log(f"Angular output: {stdout}", "ERROR")
                if stderr:
                    self.log(f"Angular error: {stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"[ERROR] Failed to start Angular server: {e}", "ERROR")
            return False

    def monitor_processes(self):
        """Monitor running processes and log their output"""
        def log_output(process_name, process):
            try:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.log(f"[{process_name}] {line.strip()}")
            except Exception as e:
                self.log(f"Error monitoring {process_name}: {e}", "ERROR")

        # Start monitoring threads for each process
        monitor_threads = []
        for process_name, process in self.processes:
            thread = threading.Thread(
                target=log_output, 
                args=(process_name, process),
                daemon=True
            )
            thread.start()
            monitor_threads.append(thread)

        # Main monitoring loop
        while self.running:
            for i, (process_name, process) in enumerate(self.processes):
                if process.poll() is not None:
                    self.log(f"[WARN] {process_name} server stopped unexpectedly", "WARN")
                    self.running = False
                    break
            time.sleep(1)

    def cleanup(self):
        """Clean up running processes"""
        self.log("[INFO] Shutting down servers...", "INFO")
        self.running = False
        
        for process_name, process in self.processes:
            try:
                self.log(f"Stopping {process_name} server...", "INFO")
                process.terminate()
                process.wait(timeout=5)
                self.log(f"[OK] {process_name} server stopped", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.log(f"Force killing {process_name} server...", "WARN")
                process.kill()
            except Exception as e:
                self.log(f"Error stopping {process_name}: {e}", "ERROR")
        
        self.log("[OK] All servers stopped", "SUCCESS")

    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.log(f"[INFO] Received signal {signum}", "INFO")
        self.cleanup()
        sys.exit(0)

    def run(self, install_deps=False, frontend_only=False, backend_only=False):
        """Main run method"""
        try:
            self.print_header()
            
            # Check prerequisites
            if not self.check_prerequisites():
                self.log("Prerequisites check failed", "ERROR")
                return False

            # Install dependencies if requested
            if install_deps:
                if not self.install_dependencies():
                    self.log("Dependency installation failed", "ERROR")
                    return False

            # Set up signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            success = True
            
            # Start backend server
            if not backend_only:
                if not self.start_backend_server():
                    success = False
            
            # Start frontend server
            if not frontend_only:
                if not self.start_frontend_server():
                    success = False
            
            if not success:
                self.log("Failed to start one or more servers", "ERROR")
                return False
            
            # Print success message
            print("\n" + "="*70)
            self.log("[SUCCESS] Development servers are running!", "SUCCESS")
            print("="*70)
            print(f"Available URLs:")
            if not frontend_only:
                print(f"   Frontend (Angular): http://localhost:{self.frontend_port}")
            if not backend_only:
                print(f"   Backend API:        http://localhost:{self.backend_port}/api/*")
                print(f"   API Health Check:   http://localhost:{self.backend_port}/api/health")
            print("="*70)
            print("Development Tips:")
            print("   - Angular changes will hot-reload automatically")
            print("   - Flask changes require server restart")
            print("   - Use Ctrl+C to stop all servers")
            print("="*70)
            
            # Monitor processes
            self.monitor_processes()
            
        except KeyboardInterrupt:
            self.log("[INFO] Keyboard interrupt received", "INFO")
        except Exception as e:
            self.log(f"[ERROR] Error: {e}", "ERROR")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run Validex development servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--frontend-port', 
        type=int, 
        default=4200,
        help='Angular dev server port (default: 4200)'
    )
    
    parser.add_argument(
        '--backend-port', 
        type=int, 
        default=8000,
        help='Flask API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--no-frontend', 
        action='store_true',
        help='Run only backend server'
    )
    
    parser.add_argument(
        '--no-backend', 
        action='store_true',
        help='Run only frontend server'
    )
    
    parser.add_argument(
        '--install-deps', 
        action='store_true',
        help='Install dependencies before starting'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.no_frontend and args.no_backend:
        print("Error: Cannot specify both --no-frontend and --no-backend")
        sys.exit(1)
    
    # Create and run the dev runner
    runner = ValidexDevRunner(
        frontend_port=args.frontend_port,
        backend_port=args.backend_port,
        debug=args.debug
    )
    
    runner.run(
        install_deps=args.install_deps,
        frontend_only=args.no_backend,
        backend_only=args.no_frontend
    )

if __name__ == '__main__':
    main()
