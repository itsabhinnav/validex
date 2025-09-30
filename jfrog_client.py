import os
import subprocess
import requests
import tempfile
from pathlib import Path
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JFrogClient:
    """JFrog Artifactory client for downloading Excel files"""
    
    def __init__(self):
        self.base_url = config.get('jfrog.base_url', '')
        self.repository = config.get('jfrog.repository', '')
        self.root_path = config.get('jfrog.root_path', '')
        self.access_token = config.get('jfrog.access_token', '')
        self.excel_files_dir = config.get('app.excel_files_dir', 'excel_files')
        
        # Ensure excel_files directory exists
        Path(self.excel_files_dir).mkdir(exist_ok=True)
    
    def is_cli_available(self):
        """Check if JFrog CLI is installed and available"""
        try:
            result = subprocess.run(['jf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def setup_cli_authentication(self):
        """Setup JFrog CLI authentication"""
        if not self.is_cli_available():
            logger.error("JFrog CLI is not available")
            return False
        
        try:
            # Configure JFrog CLI with the access token using proper encoding
            cmd = [
                'jf', 'c', 'add', 'validex-config',
                '--url', self.base_url,
                '--access-token', self.access_token
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', timeout=30)
            
            if result.returncode == 0:
                logger.info("JFrog CLI authentication configured successfully")
                return True
            else:
                logger.error(f"Failed to configure JFrog CLI: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("JFrog CLI authentication timed out")
            return False
        except Exception as e:
            logger.error(f"Error setting up JFrog CLI authentication: {e}")
            return False
    
    def download_file_via_cli(self, file_path, local_filename=None):
        """Download file using JFrog CLI"""
        if not self.is_cli_available():
            logger.error("JFrog CLI is not available")
            return None
        
        try:
            # Setup authentication if not already done
            if not self.setup_cli_authentication():
                return None
            
            # Construct the full repository path
            full_path = f"{self.repository}/{self.root_path}/{file_path}" if self.root_path else f"{self.repository}/{file_path}"
            
            # Set local filename if not provided
            if local_filename is None:
                local_filename = os.path.basename(file_path)
            
            local_file_path = Path(self.excel_files_dir) / local_filename
            
            # Download using JFrog CLI
            cmd = [
                'jf', 'rt', 'download',
                full_path,
                str(local_file_path.parent) + '/',
                '--server-id', 'validex-config'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded {file_path} to {local_file_path}")
                return local_file_path
            else:
                logger.error(f"Failed to download {file_path}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Download of {file_path} timed out")
            return None
        except Exception as e:
            logger.error(f"Error downloading {file_path} via CLI: {e}")
            return None
    
    def download_file_via_api(self, file_path, local_filename=None):
        """Download file using JFrog REST API"""
        try:
            # Construct the full URL
            full_url = f"{self.base_url}/{self.repository}/{self.root_path}/{file_path}" if self.root_path else f"{self.base_url}/{self.repository}/{file_path}"
            
            # Set local filename if not provided
            if local_filename is None:
                local_filename = os.path.basename(file_path)
            
            local_file_path = Path(self.excel_files_dir) / local_filename
            
            # Download using requests
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': 'Validex/1.0'
            }
            
            response = requests.get(full_url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save file
            with open(local_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded {file_path} to {local_file_path}")
            return local_file_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {file_path} via API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading {file_path} via API: {e}")
            return None
    
    def download_file(self, file_path, local_filename=None):
        """Download file using best available method (CLI preferred, API fallback)"""
        if self.is_cli_available():
            logger.info(f"Downloading {file_path} using JFrog CLI")
            result = self.download_file_via_cli(file_path, local_filename)
            if result:
                return result
            else:
                logger.warning(f"CLI download failed, trying API for {file_path}")
        
        logger.info(f"Downloading {file_path} using JFrog API")
        return self.download_file_via_api(file_path, local_filename)
    
    def list_excel_files(self):
        """List all Excel files in the repository root path"""
        try:
            # Construct the search path
            search_path = f"{self.repository}/{self.root_path}" if self.root_path else self.repository
            
            if self.is_cli_available():
                try:
                    # Use CLI to list files with proper encoding
                    cmd = [
                        'jf', 'rt', 'search',
                        search_path + '/*.xlsx',
                        '--server-id', 'validex-config'
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, 
                                          encoding='utf-8', errors='ignore', timeout=30)
                    
                    if result.returncode == 0:
                        files = []
                        for line in result.stdout.strip().split('\n'):
                            if line.strip() and '.xlsx' in line:
                                # Extract filename from the output
                                filename = line.split('/')[-1]
                                if filename.endswith('.xlsx'):
                                    files.append(filename)
                        if files:
                            logger.info(f"Found {len(files)} Excel files via CLI: {files}")
                            return files
                except Exception as cli_error:
                    logger.warning(f"CLI search failed: {cli_error}")
            
            # Fallback: Use JFrog REST API to search for files
            try:
                api_url = f"{self.base_url}/api/search/aql"
                
                # Construct AQL query to find all Excel files
                aql_query = f"""
                items.find({{
                    "repo": "{self.repository}",
                    "path": {{"$match": "{self.root_path}/*"}} if "{self.root_path}" else {{"$match": "*"}},
                    "name": {{"$match": "*.xlsx"}}
                }}).include("name", "path")
                """
                
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'text/plain'
                }
                
                response = requests.post(api_url, data=aql_query, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    files = []
                    
                    for item in data.get('results', []):
                        filename = item.get('name', '')
                        if filename.endswith('.xlsx'):
                            files.append(filename)
                    
                    if files:
                        logger.info(f"Found {len(files)} Excel files via API: {files}")
                        return files
                        
            except Exception as api_error:
                logger.warning(f"API search failed: {api_error}")
            
            # Last resort: return known files
            logger.warning("Using fallback file list")
            return ['banking_test_cases.xlsx']
            
        except Exception as e:
            logger.error(f"Error listing Excel files: {e}")
            return ['banking_test_cases.xlsx']
    
    def clear_local_files(self):
        """Clear all local Excel files"""
        try:
            if not os.path.exists(self.excel_files_dir):
                return
            
            excel_files = [f for f in os.listdir(self.excel_files_dir) if f.endswith(('.xlsx', '.xls'))]
            
            for filename in excel_files:
                file_path = Path(self.excel_files_dir) / filename
                try:
                    file_path.unlink()
                    logger.info(f"Deleted local file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")
                    
        except Exception as e:
            logger.error(f"Error clearing local files: {e}")

    def sync_excel_files(self):
        """Sync all Excel files from JFrog repository"""
        if not config.is_jfrog_enabled():
            logger.info("JFrog integration is disabled")
            return []
        
        logger.info("Starting JFrog Excel files sync")
        
        # Clear existing local files first
        self.clear_local_files()
        
        # List all Excel files in the repository
        excel_files = self.list_excel_files()
        
        if not excel_files:
            logger.warning("No Excel files found in JFrog repository")
            return []
        
        downloaded_files = []
        failed_files = []
        
        for filename in excel_files:
            logger.info(f"Processing file: {filename}")
            
            # Download the file (always download fresh)
            result = self.download_file(filename)
            if result:
                downloaded_files.append(str(result))
                logger.info(f"Successfully synced {filename}")
            else:
                logger.error(f"Failed to sync {filename}")
                failed_files.append(filename)
        
        logger.info(f"JFrog sync completed:")
        logger.info(f"  - Downloaded: {len(downloaded_files)} files")
        logger.info(f"  - Failed: {len(failed_files)} files")
        
        if failed_files:
            logger.error(f"Failed files: {failed_files}")
        
        return downloaded_files

# Global JFrog client instance
jfrog_client = JFrogClient()
