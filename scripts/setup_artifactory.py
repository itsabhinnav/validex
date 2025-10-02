#!/usr/bin/env python3
"""
JFrog Artifactory Setup Script for Validex
This script helps configure and sync with JFrog Artifactory
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class ArtifactorySetup:
    """Setup and sync with JFrog Artifactory"""
    
    def __init__(self):
        self.config_file = Path("config/validex_config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_user_input(self):
        """Get Artifactory configuration from user"""
        print("🔧 JFrog Artifactory Configuration Setup")
        print("=" * 50)
        
        # Get Artifactory URL
        base_url = input("Enter your Artifactory URL (e.g., https://your-company.jfrog.io/artifactory): ").strip()
        if not base_url:
            print("❌ Artifactory URL is required!")
            return False
        
        # Get repository name
        repository = input("Enter repository name: ").strip()
        if not repository:
            print("❌ Repository name is required!")
            return False
        
        # Get root path
        root_path = input("Enter project root path (e.g., test-cases, validex): ").strip()
        
        # Get access token
        access_token = input("Enter your Artifactory access token: ").strip()
        if not access_token:
            print("❌ Access token is required!")
            return False
        
        # Update configuration
        self.config["jfrog"] = {
            "base_url": base_url,
            "repository": repository,
            "root_path": root_path,
            "access_token": access_token,
            "enabled": True
        }
        
        self.config["app"] = {
            "excel_files_dir": "data/excel_files",
            "reports_dir": "data/reports",
            "auto_refresh_interval": 30
        }
        
        return True
    
    def test_connection(self) -> bool:
        """Test connection to Artifactory"""
        print("\n🔍 Testing Artifactory connection...")
        
        try:
            jfrog_config = self.config.get("jfrog", {})
            base_url = jfrog_config.get("base_url", "").rstrip('/')
            repository = jfrog_config.get("repository", "")
            access_token = jfrog_config.get("access_token", "")
            
            # Test API connection
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to list repository contents
            api_url = f"{base_url}/api/storage/{repository}"
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ Successfully connected to Artifactory!")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def list_remote_files(self) -> list:
        """List files available in Artifactory"""
        print("\n📁 Listing files in Artifactory...")
        
        try:
            jfrog_config = self.config.get("jfrog", {})
            base_url = jfrog_config.get("base_url", "").rstrip('/')
            repository = jfrog_config.get("repository", "")
            root_path = jfrog_config.get("root_path", "")
            access_token = jfrog_config.get("access_token", "")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Build API URL
            if root_path:
                api_url = f"{base_url}/api/storage/{repository}/{root_path}"
            else:
                api_url = f"{base_url}/api/storage/{repository}"
            
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                files = []
                
                # Extract file information
                for item in data.get('children', []):
                    if item.get('folder', False):
                        # It's a folder, we'll need to explore it
                        folder_path = item.get('uri', '').lstrip('/')
                        print(f"📁 Found folder: {folder_path}")
                    else:
                        # It's a file
                        file_path = item.get('uri', '').lstrip('/')
                        if file_path.endswith(('.xlsx', '.xls', '.db')):
                            files.append(file_path)
                            print(f"📄 Found file: {file_path}")
                
                return files
            else:
                print(f"❌ Failed to list files: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []
    
    def download_files(self, files: list) -> bool:
        """Download files from Artifactory"""
        print(f"\n⬇️ Downloading {len(files)} files from Artifactory...")
        
        try:
            jfrog_config = self.config.get("jfrog", {})
            base_url = jfrog_config.get("base_url", "").rstrip('/')
            repository = jfrog_config.get("repository", "")
            root_path = jfrog_config.get("root_path", "")
            access_token = jfrog_config.get("access_token", "")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Create local directories
            os.makedirs("data/excel_files", exist_ok=True)
            os.makedirs("data/reports", exist_ok=True)
            
            downloaded_count = 0
            
            for file_path in files:
                try:
                    # Build download URL
                    if root_path:
                        download_url = f"{base_url}/{repository}/{root_path}/{file_path}"
                    else:
                        download_url = f"{base_url}/{repository}/{file_path}"
                    
                    # Download file
                    response = requests.get(download_url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        # Determine local path
                        if file_path.endswith('.db'):
                            local_path = f"data/{file_path}"
                        else:
                            local_path = f"data/excel_files/{file_path}"
                        
                        # Create directory if needed
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        
                        # Save file
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"✅ Downloaded: {file_path}")
                        downloaded_count += 1
                    else:
                        print(f"❌ Failed to download {file_path}: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error downloading {file_path}: {e}")
            
            print(f"\n📊 Download Summary: {downloaded_count}/{len(files)} files downloaded")
            return downloaded_count > 0
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def setup_environment(self):
        """Setup environment variables"""
        print("\n🔧 Setting up environment variables...")
        
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            env_content = """# Validex Environment Configuration
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
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Created .env file")
        else:
            print("ℹ️ .env file already exists")
    
    def initialize_database(self):
        """Initialize database if needed"""
        print("\n🗄️ Initializing database...")
        
        try:
            # Import and initialize database
            sys.path.insert(0, '.')
            from app import create_app
            from app.services.database_service import DatabaseService
            
            app = create_app('production')
            with app.app_context():
                db_service = DatabaseService()
                db_service.initialize()
                print("✅ Database initialized successfully")
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 Validex JFrog Artifactory Setup")
        print("=" * 50)
        
        # Step 1: Get user input
        if not self.get_user_input():
            print("❌ Setup cancelled")
            return False
        
        # Step 2: Save configuration
        self.save_config()
        print("✅ Configuration saved")
        
        # Step 3: Test connection
        if not self.test_connection():
            print("❌ Setup failed - cannot connect to Artifactory")
            return False
        
        # Step 4: List and download files
        files = self.list_remote_files()
        if not files:
            print("⚠️ No Excel or database files found in Artifactory")
            print("Make sure your files are uploaded to the correct path")
            return False
        
        if not self.download_files(files):
            print("❌ Failed to download files")
            return False
        
        # Step 5: Setup environment
        self.setup_environment()
        
        # Step 6: Initialize database
        self.initialize_database()
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Access the application: http://localhost:8000")
        print("3. Your Excel files are now available in data/excel_files/")
        
        return True

def main():
    """Main function"""
    setup = ArtifactorySetup()
    setup.run_setup()

if __name__ == "__main__":
    main()

