"""
Excel File Processing Service for High-Performance Bulk Import
Handles large-scale Excel file processing with optimization
"""

import pandas as pd
import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

class ExcelProcessingService:
    """High-performance Excel file processing service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.batch_size = 10000
        self.max_workers = 4
        
    def discover_excel_files(self, directory: str) -> List[Path]:
        """Discover all Excel files in directory recursively"""
        excel_dir = Path(directory)
        
        if not excel_dir.exists():
            self.logger.warning(f"Excel directory not found: {directory}")
            return []
        
        # Find all Excel files
        excel_files = []
        for pattern in ['*.xlsx', '*.xls']:
            excel_files.extend(excel_dir.rglob(pattern))
        
        self.logger.info(f"Discovered {len(excel_files)} Excel files")
        return excel_files
    
    def analyze_excel_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Excel file structure and content"""
        try:
            start_time = time.time()
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            analysis = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_hash': self._calculate_file_hash(file_path),
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'sample_data': df.head(3).to_dict('records'),
                'processing_time': time.time() - start_time,
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            }
            
            # Analyze column patterns
            analysis['column_analysis'] = self._analyze_columns(df)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'processing_time': 0
            }
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze column patterns and data quality"""
        analysis = {}
        
        for column in df.columns:
            col_data = df[column].dropna()
            
            analysis[column] = {
                'total_values': len(df[column]),
                'non_null_values': len(col_data),
                'null_count': df[column].isnull().sum(),
                'unique_count': col_data.nunique(),
                'data_type': str(df[column].dtype),
                'sample_values': col_data.head(5).tolist() if len(col_data) > 0 else []
            }
            
            # Check for common test case patterns
            if column.lower() in ['tc id', 'test case id', 'test_case_id']:
                analysis[column]['is_primary_key'] = True
                analysis[column]['pattern'] = self._analyze_id_pattern(col_data)
            elif column.lower() in ['priority']:
                analysis[column]['allowed_values'] = col_data.unique().tolist()
            elif column.lower() in ['status']:
                analysis[column]['allowed_values'] = col_data.unique().tolist()
        
        return analysis
    
    def _analyze_id_pattern(self, id_series: pd.Series) -> Dict[str, Any]:
        """Analyze ID pattern for test cases"""
        patterns = {
            'format': 'unknown',
            'prefixes': [],
            'separators': [],
            'length_stats': {}
        }
        
        if len(id_series) == 0:
            return patterns
        
        # Analyze first few IDs for pattern
        sample_ids = id_series.head(10).astype(str)
        
        for id_val in sample_ids:
            if '_' in id_val:
                patterns['separators'].append('_')
                parts = id_val.split('_')
                if len(parts) >= 2:
                    patterns['prefixes'].append(parts[0])
            elif '-' in id_val:
                patterns['separators'].append('-')
                parts = id_val.split('-')
                if len(parts) >= 2:
                    patterns['prefixes'].append(parts[0])
        
        # Determine format
        if '_' in patterns['separators']:
            patterns['format'] = 'underscore_separated'
        elif '-' in patterns['separators']:
            patterns['format'] = 'dash_separated'
        
        patterns['prefixes'] = list(set(patterns['prefixes']))
        patterns['separators'] = list(set(patterns['separators']))
        
        return patterns
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return hashlib.sha256(str(file_path).encode()).hexdigest()
    
    def validate_excel_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate Excel file for test case import"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                validation['is_valid'] = False
                validation['errors'].append("File is empty")
                return validation
            
            # Check for required columns
            required_columns = ['TC ID', 'Test Case ID']
            has_primary_key = any(col in df.columns for col in required_columns)
            
            if not has_primary_key:
                validation['is_valid'] = False
                validation['errors'].append("No primary key column found (TC ID or Test Case ID)")
            
            # Check for duplicate IDs
            id_column = None
            for col in required_columns:
                if col in df.columns:
                    id_column = col
                    break
            
            if id_column:
                duplicates = df[id_column].duplicated().sum()
                if duplicates > 0:
                    validation['warnings'].append(f"Found {duplicates} duplicate {id_column} values")
            
            # Check for empty required fields
            if 'Summary' in df.columns:
                empty_summaries = df['Summary'].isnull().sum()
                if empty_summaries > 0:
                    validation['warnings'].append(f"Found {empty_summaries} empty Summary fields")
            
            # Recommendations
            if 'Priority' not in df.columns:
                validation['recommendations'].append("Consider adding Priority column")
            
            if 'Status' not in df.columns:
                validation['recommendations'].append("Consider adding Status column")
            
            if 'Expected Behavior' not in df.columns:
                validation['recommendations'].append("Consider adding Expected Behavior column")
            
        except Exception as e:
            validation['is_valid'] = False
            validation['errors'].append(f"Error reading file: {str(e)}")
        
        return validation
    
    def process_excel_batch(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process a batch of Excel files in parallel"""
        start_time = time.time()
        
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(file_paths),
            'total_records': 0,
            'processing_time': 0
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path 
                for file_path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['successful'].append({
                            'file_path': str(file_path),
                            'record_count': result['record_count'],
                            'processing_time': result['processing_time']
                        })
                        results['total_records'] += result['record_count']
                    else:
                        results['failed'].append({
                            'file_path': str(file_path),
                            'error': result['error']
                        })
                except Exception as e:
                    results['failed'].append({
                        'file_path': str(file_path),
                        'error': str(e)
                    })
        
        results['processing_time'] = time.time() - start_time
        results['success_rate'] = len(results['successful']) / len(file_paths) * 100 if file_paths else 0
        
        return results
    
    def _process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single Excel file"""
        try:
            start_time = time.time()
            
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {
                    'success': True,
                    'record_count': 0,
                    'processing_time': time.time() - start_time,
                    'message': 'Empty file'
                }
            
            # Convert to records
            records = df.to_dict('records')
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'record_count': len(records),
                'processing_time': processing_time,
                'file_hash': self._calculate_file_hash(file_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'record_count': 0,
                'processing_time': 0
            }
    
    def get_file_statistics(self, directory: str) -> Dict[str, Any]:
        """Get comprehensive statistics about Excel files in directory"""
        excel_files = self.discover_excel_files(directory)
        
        if not excel_files:
            return {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'directory_structure': {}
            }
        
        stats = {
            'total_files': len(excel_files),
            'total_size': sum(f.stat().st_size for f in excel_files),
            'file_types': {},
            'directory_structure': {},
            'largest_files': [],
            'oldest_files': [],
            'newest_files': []
        }
        
        # Analyze file types
        for file_path in excel_files:
            ext = file_path.suffix.lower()
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
        
        # Analyze directory structure
        for file_path in excel_files:
            relative_path = file_path.relative_to(Path(directory))
            parts = relative_path.parts[:-1]  # Exclude filename
            
            current = stats['directory_structure']
            for part in parts:
                if part not in current:
                    current[part] = {'files': 0, 'subdirs': {}}
                current[part]['files'] += 1
                current = current[part]['subdirs']
        
        # Get largest files
        file_sizes = [(f, f.stat().st_size) for f in excel_files]
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        stats['largest_files'] = [
            {'file': str(f), 'size': size} 
            for f, size in file_sizes[:10]
        ]
        
        # Get oldest and newest files
        file_times = [(f, f.stat().st_mtime) for f in excel_files]
        file_times.sort(key=lambda x: x[1])
        
        stats['oldest_files'] = [
            {'file': str(f), 'modified': datetime.fromtimestamp(t)} 
            for f, t in file_times[:5]
        ]
        
        stats['newest_files'] = [
            {'file': str(f), 'modified': datetime.fromtimestamp(t)} 
            for f, t in file_times[-5:]
        ]
        
        return stats
