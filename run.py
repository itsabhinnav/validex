"""
Test Case Management System - Application Entry Point

Copyright 2025 Validex Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app

def main():
    """Main application entry point"""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config_name)
    
    # Get host and port from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    print("Starting Test Case Management System")
    print(f"Environment: {config_name}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug: {debug}")
    print(f"Working Directory: {project_root}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
