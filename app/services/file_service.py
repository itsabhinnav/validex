"""
File service for Test Case Management System
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.models.test_case import TestCase
from app.models.file_metadata import FileMetadata

class FileService:
    """Service for file operations"""
    
    def __init__(self, upload_folder: str = "data/excel_files"):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def process_excel_file(self, file_path: str, base_dir: str = None) -> List[TestCase]:
        """Process an Excel file and return test cases"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Get relative path
            if base_dir:
                relative_path = os.path.relpath(file_path, base_dir)
            else:
                relative_path = os.path.basename(file_path)
            
            # Extract path parts
            path_parts = relative_path.split(os.sep)
            app_name = path_parts[0] if len(path_parts) > 0 else 'Unknown'
            test_category = path_parts[1] if len(path_parts) > 1 else 'Unknown'
            directory_structure = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
            
            # Convert to test cases
            test_cases = []
            for _, row in df.iterrows():
                test_case = TestCase(
                    tc_id=row.get('TC ID', ''),
                    summary=row.get('Summary', ''),
                    feature=row.get('Feature', ''),
                    priority=row.get('Priority', ''),
                    status=row.get('Status', ''),
                    screen_id=row.get('Screen ID', ''),
                    test_type=row.get('type', ''),
                    expected_behavior=row.get('Expected Behavior', ''),
                    procedure=row.get('Procedure', ''),
                    preconditions=row.get('Preconditions', ''),
                    file_path=relative_path,
                    directory_structure=directory_structure,
                    app_name=app_name,
                    test_category=test_category
                )
                test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate file hash for change detection"""
        try:
            import hashlib
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def is_file_changed(self, file_path: str, stored_hash: str) -> bool:
        """Check if file has changed"""
        current_hash = self.get_file_hash(file_path)
        return current_hash != stored_hash if current_hash else True
    
    def scan_directory(self, directory: str) -> List[str]:
        """Scan directory for Excel files"""
        excel_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return excel_files
        
        for file_path in directory_path.rglob('*.xlsx'):
            excel_files.append(str(file_path))
        
        for file_path in directory_path.rglob('*.xls'):
            excel_files.append(str(file_path))
        
        return excel_files
    
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Get file metadata"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None
            
            stat = file_path_obj.stat()
            file_hash = self.get_file_hash(file_path)
            
            return FileMetadata(
                file_id=str(file_path_obj),
                file_path=str(file_path_obj),
                file_hash=file_hash or '',
                file_size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                local_path=str(file_path_obj)
            )
            
        except Exception as e:
            print(f"Error getting metadata for {file_path}: {e}")
            return None
    
    def validate_excel_file(self, file_path: str) -> bool:
        """Validate Excel file format"""
        try:
            df = pd.read_excel(file_path)
            
            # Check for required columns
            required_columns = ['TC ID', 'Summary', 'Feature', 'Priority', 'Status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Missing required columns: {missing_columns}")
                return False
            
            # Check if file has data
            if df.empty:
                print("File is empty")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating file {file_path}: {e}")
            return False
    
    def get_file_statistics(self, file_path: str) -> Dict[str, Any]:
        """Get file statistics"""
        try:
            df = pd.read_excel(file_path)
            
            return {
                'total_rows': len(df),
                'columns': list(df.columns),
                'file_size': os.path.getsize(file_path),
                'last_modified': os.path.getmtime(file_path)
            }
            
        except Exception as e:
            print(f"Error getting statistics for {file_path}: {e}")
            return {}

