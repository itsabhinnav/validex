"""
High Performance Database Service for 1M+ Test Cases
Optimized for fast searching, filtering, and bulk operations
"""

import sqlite3
import os
import threading
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.path_resolver import path_resolver
from app.models.test_case import TestCase
from app.models.file_metadata import FileMetadata

class HighPerformanceDatabaseService:
    """High-performance database service optimized for 1M+ test cases"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(path_resolver.get_database_path())
        self._local = threading.local()
        self._connection_pool = []
        self._pool_lock = threading.Lock()
        self._max_connections = 20
        self._ensure_data_directory()
        
        # Performance settings
        self.batch_size = 10000  # Batch size for bulk operations
        self.index_batch_size = 5000  # Batch size for index creation
        
    def _get_connection(self):
        """Get thread-local database connection with performance optimizations"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
            
            # Performance optimizations
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            self._local.connection.execute("PRAGMA synchronous=NORMAL")
            self._local.connection.execute("PRAGMA cache_size=10000")
            self._local.connection.execute("PRAGMA temp_store=MEMORY")
            self._local.connection.execute("PRAGMA mmap_size=268435456")  # 256MB
            self._local.connection.execute("PRAGMA optimize")
            
        return self._local.connection
    
    def _close_connection(self):
        """Close thread-local database connection"""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        try:
            data_dir = Path(self.db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"High-performance data directory ensured: {data_dir}")
        except Exception as e:
            print(f"Error creating data directory: {e}")
            raise

    def initialize(self):
        """Initialize high-performance database with optimized schema"""
        try:
            print("Initializing high-performance database...")
            self._create_optimized_tables()
            self._create_performance_indexes()
            self._analyze_database()
            print("High-performance database initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing high-performance database: {e}")
            return False

    def _create_optimized_tables(self):
        """Create optimized tables for high-performance operations"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        # Drop existing tables if they exist (for fresh start)
        cursor.execute("DROP TABLE IF EXISTS test_cases")
        cursor.execute("DROP TABLE IF EXISTS file_metadata")
        cursor.execute("DROP TABLE IF EXISTS test_case_index")
        cursor.execute("DROP TABLE IF EXISTS search_cache")
        
        # Create optimized test_cases table
        cursor.execute('''
            CREATE TABLE test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_id TEXT NOT NULL UNIQUE,
                summary TEXT,
                feature TEXT,
                priority TEXT,
                status TEXT,
                screen_id TEXT,
                test_type TEXT,
                expected_behavior TEXT,
                procedure TEXT,
                preconditions TEXT,
                file_path TEXT,
                directory_structure TEXT,
                app_name TEXT,
                test_category TEXT,
                file_id TEXT,
                local_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Additional columns for comprehensive test case data
                reference_document TEXT,
                associated_requirements TEXT,
                dr_applicable_screens TEXT,
                test_objective TEXT,
                test_suite_type TEXT,
                requirement_type TEXT,
                region TEXT,
                brand TEXT,
                test_data TEXT,
                test_environment TEXT,
                automation_status TEXT,
                execution_time REAL,
                last_executed TIMESTAMP,
                execution_count INTEGER DEFAULT 0,
                pass_rate REAL DEFAULT 0.0,
                
                -- Metadata for performance
                file_hash TEXT,
                row_number INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create file metadata table
        cursor.execute('''
            CREATE TABLE file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_hash TEXT,
                file_size INTEGER,
                last_modified TIMESTAMP,
                last_synced TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                record_count INTEGER DEFAULT 0,
                processing_time REAL,
                error_message TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create search cache table for frequently accessed data
        cursor.execute('''
            CREATE TABLE search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                cache_data TEXT NOT NULL,
                cache_type TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create test case index table for fast lookups
        cursor.execute('''
            CREATE TABLE test_case_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_id TEXT NOT NULL,
                searchable_text TEXT,
                feature_normalized TEXT,
                priority_normalized TEXT,
                status_normalized TEXT,
                app_normalized TEXT,
                test_type_normalized TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        connection.commit()
        print("Optimized tables created successfully")

    def _create_performance_indexes(self):
        """Create comprehensive indexes for maximum performance"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        print("Creating performance indexes...")
        
        # Primary lookup indexes
        indexes = [
            # Core indexes for test cases
            "CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id)",
            "CREATE INDEX IF NOT EXISTS idx_tc_id_active ON test_cases(tc_id, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature)",
            "CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority)",
            "CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status)",
            "CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name)",
            "CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type)",
            "CREATE INDEX IF NOT EXISTS idx_screen_id ON test_cases(screen_id)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_feature_priority ON test_cases(feature, priority)",
            "CREATE INDEX IF NOT EXISTS idx_app_status ON test_cases(app_name, status)",
            "CREATE INDEX IF NOT EXISTS idx_feature_status ON test_cases(feature, status)",
            "CREATE INDEX IF NOT EXISTS idx_priority_status ON test_cases(priority, status)",
            
            # Full-text search indexes
            "CREATE INDEX IF NOT EXISTS idx_summary_ft ON test_cases(summary)",
            "CREATE INDEX IF NOT EXISTS idx_expected_behavior_ft ON test_cases(expected_behavior)",
            "CREATE INDEX IF NOT EXISTS idx_procedure_ft ON test_cases(procedure)",
            
            # File and metadata indexes
            "CREATE INDEX IF NOT EXISTS idx_file_path ON test_cases(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON test_cases(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_updated_at ON test_cases(updated_at)",
            
            # File metadata indexes
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_hash ON file_metadata(file_hash)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_status ON file_metadata(sync_status)",
            
            # Search cache indexes
            "CREATE INDEX IF NOT EXISTS idx_cache_key ON search_cache(cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_at)",
            
            # Test case index table indexes
            "CREATE INDEX IF NOT EXISTS idx_index_tc_id ON test_case_index(tc_id)",
            "CREATE INDEX IF NOT EXISTS idx_searchable_text ON test_case_index(searchable_text)",
            "CREATE INDEX IF NOT EXISTS idx_feature_norm ON test_case_index(feature_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_priority_norm ON test_case_index(priority_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_status_norm ON test_case_index(status_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_app_norm ON test_case_index(app_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_test_type_norm ON test_case_index(test_type_normalized)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"Warning: Could not create index: {e}")
        
        connection.commit()
        print(f"Created {len(indexes)} performance indexes")

    def _analyze_database(self):
        """Analyze database for optimal query planning"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("ANALYZE")
            print("Database analysis completed")
        except Exception as e:
            print(f"Warning: Database analysis failed: {e}")

    def bulk_import_excel_files(self, excel_directory: str) -> Dict[str, Any]:
        """Bulk import all Excel files from directory with high performance"""
        start_time = time.time()
        excel_dir = Path(excel_directory)
        
        if not excel_dir.exists():
            return {
                'success': False,
                'message': f'Excel directory not found: {excel_directory}',
                'files_processed': 0,
                'total_records': 0,
                'processing_time': 0
            }
        
        # Find all Excel files recursively
        excel_files = list(excel_dir.rglob('*.xlsx'))
        print(f"Found {len(excel_files)} Excel files to process")
        
        total_records = 0
        files_processed = 0
        errors = []
        
        # Process files in batches for better performance
        batch_size = 5  # Process 5 files at a time
        for i in range(0, len(excel_files), batch_size):
            batch_files = excel_files[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                future_to_file = {
                    executor.submit(self._process_excel_file, file_path): file_path 
                    for file_path in batch_files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result['success']:
                            files_processed += 1
                            total_records += result['record_count']
                            print(f"Processed {file_path.name}: {result['record_count']} records")
                        else:
                            errors.append(f"{file_path.name}: {result['error']}")
                    except Exception as e:
                        errors.append(f"{file_path.name}: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Update search indexes after bulk import
        self._update_search_indexes()
        
        return {
            'success': True,
            'message': f'Bulk import completed',
            'files_processed': files_processed,
            'total_records': total_records,
            'processing_time': round(processing_time, 2),
            'errors': errors,
            'files_per_second': round(files_processed / processing_time, 2) if processing_time > 0 else 0,
            'records_per_second': round(total_records / processing_time, 2) if processing_time > 0 else 0
        }

    def _process_excel_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single Excel file and import to database"""
        try:
            start_time = time.time()
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {
                    'success': True,
                    'record_count': 0,
                    'message': 'Empty file'
                }
            
            # Generate file metadata
            file_hash = self._calculate_file_hash(file_path)
            file_id = f"{file_path.stem}_{file_hash[:8]}"
            
            # Prepare data for bulk insert
            records = []
            for index, row in df.iterrows():
                record = self._prepare_test_case_record(row, file_path, file_id, index + 1)
                records.append(record)
            
            # Bulk insert to database
            self._bulk_insert_test_cases(records)
            
            # Update file metadata
            self._update_file_metadata(file_path, file_id, file_hash, len(records))
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'record_count': len(records),
                'processing_time': processing_time,
                'file_id': file_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'record_count': 0
            }

    def _prepare_test_case_record(self, row: pd.Series, file_path: Path, file_id: str, row_number: int) -> Dict[str, Any]:
        """Prepare a test case record for database insertion"""
        # Normalize column names and handle missing values
        record = {
            'tc_id': str(row.get('TC ID', row.get('Test Case ID', f'TC_{file_id}_{row_number}'))),
            'summary': str(row.get('Summary', row.get('Test Objective', ''))),
            'feature': str(row.get('Feature', '')),
            'priority': str(row.get('Priority', 'Medium')),
            'status': str(row.get('Status', 'Pending')),
            'screen_id': str(row.get('Screen ID', '')),
            'test_type': str(row.get('Test Type', '')),
            'expected_behavior': str(row.get('Expected Behavior', '')),
            'procedure': str(row.get('Procedure', '')),
            'preconditions': str(row.get('Preconditions', '')),
            'file_path': str(file_path),
            'directory_structure': str(file_path.parent.relative_to(file_path.parents[2])),
            'app_name': str(row.get('App', '')),
            'test_category': str(row.get('Test Category', '')),
            'file_id': file_id,
            'row_number': row_number,
            'file_hash': self._calculate_file_hash(file_path),
            
            # Additional columns
            'reference_document': str(row.get('Reference Document', '')),
            'associated_requirements': str(row.get('Associated Requirements', '')),
            'dr_applicable_screens': str(row.get('DR Applicable Screens', '')),
            'test_objective': str(row.get('Test Objective', '')),
            'test_suite_type': str(row.get('TestSuite Type', '')),
            'requirement_type': str(row.get('Requirement Type', '')),
            'region': str(row.get('Region', '')),
            'brand': str(row.get('Brand', '')),
            'test_data': str(row.get('Test Data', '')),
            'test_environment': str(row.get('Test Environment', '')),
            'automation_status': str(row.get('Automation Status', '')),
            
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return record

    def _bulk_insert_test_cases(self, records: List[Dict[str, Any]]):
        """Bulk insert test cases with optimal performance"""
        if not records:
            return
        
        connection = self._get_connection()
        cursor = connection.cursor()
        
        # Prepare SQL for bulk insert
        columns = list(records[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT OR REPLACE INTO test_cases ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Convert records to tuples for bulk insert
        values = [tuple(record[col] for col in columns) for record in records]
        
        # Execute in batches for better performance
        batch_size = self.batch_size
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            cursor.executemany(sql, batch)
        
        connection.commit()

    def _update_file_metadata(self, file_path: Path, file_id: str, file_hash: str, record_count: int):
        """Update file metadata in database"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        metadata = {
            'file_id': file_id,
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_hash': file_hash,
            'file_size': file_path.stat().st_size,
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime),
            'last_synced': datetime.now(),
            'sync_status': 'completed',
            'record_count': record_count,
            'processing_time': 0.0,
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        columns = list(metadata.keys())
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT OR REPLACE INTO file_metadata ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor.execute(sql, tuple(metadata[col] for col in columns))
        connection.commit()

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

    def _update_search_indexes(self):
        """Update search indexes for fast searching"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        print("Updating search indexes...")
        
        # Clear existing indexes
        cursor.execute("DELETE FROM test_case_index")
        
        # Create search indexes for all test cases
        cursor.execute("""
            INSERT INTO test_case_index (
                tc_id, searchable_text, feature_normalized, priority_normalized,
                status_normalized, app_normalized, test_type_normalized
            )
            SELECT 
                tc_id,
                LOWER(COALESCE(summary, '') || ' ' || COALESCE(expected_behavior, '') || ' ' || COALESCE(procedure, '')),
                LOWER(COALESCE(feature, '')),
                LOWER(COALESCE(priority, '')),
                LOWER(COALESCE(status, '')),
                LOWER(COALESCE(app_name, '')),
                LOWER(COALESCE(test_type, ''))
            FROM test_cases 
            WHERE is_active = 1
        """)
        
        connection.commit()
        print("Search indexes updated successfully")

    def fast_search(self, query: str, filters: Dict[str, Any] = None, 
                   limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        """Fast search with advanced filtering and pagination"""
        start_time = time.time()
        
        connection = self._get_connection()
        cursor = connection.cursor()
        
        # Build dynamic WHERE clause
        where_conditions = ["tc.is_active = 1"]
        params = []
        
        # Text search
        if query:
            where_conditions.append("tc.tc_id LIKE ? OR tc.summary LIKE ? OR tc.expected_behavior LIKE ?")
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if value and field in ['feature', 'priority', 'status', 'app_name', 'test_type', 'screen_id']:
                    where_conditions.append(f"tc.{field} = ?")
                    params.append(value)
        
        where_clause = " AND ".join(where_conditions)
        
        # Count total results
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM test_cases tc
            WHERE {where_clause}
        """
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()['total']
        
        # Get paginated results
        search_sql = f"""
            SELECT tc.*, fm.file_name, fm.last_modified as file_last_modified
            FROM test_cases tc
            LEFT JOIN file_metadata fm ON tc.file_id = fm.file_id
            WHERE {where_clause}
            ORDER BY tc.tc_id
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(search_sql, params + [limit, offset])
        results = [dict(row) for row in cursor.fetchall()]
        
        search_time = time.time() - start_time
        
        return {
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(results) < total_count,
            'search_time': round(search_time, 4),
            'query': query,
            'filters': filters or {}
        }

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get all available filter options for UI"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        filter_fields = ['feature', 'priority', 'status', 'app_name', 'test_type', 'screen_id']
        options = {}
        
        for field in filter_fields:
            cursor.execute(f"""
                SELECT DISTINCT {field} as value, COUNT(*) as count
                FROM test_cases 
                WHERE is_active = 1 AND {field} IS NOT NULL AND {field} != ''
                GROUP BY {field}
                ORDER BY count DESC, {field}
            """)
            
            options[field] = [row['value'] for row in cursor.fetchall()]
        
        return options

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        stats = {}
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) as total FROM test_cases WHERE is_active = 1")
        stats['total_test_cases'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM file_metadata WHERE is_active = 1")
        stats['total_files'] = cursor.fetchone()['total']
        
        # Status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM test_cases 
            WHERE is_active = 1
            GROUP BY status
            ORDER BY count DESC
        """)
        stats['status_distribution'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Priority distribution
        cursor.execute("""
            SELECT priority, COUNT(*) as count
            FROM test_cases 
            WHERE is_active = 1
            GROUP BY priority
            ORDER BY count DESC
        """)
        stats['priority_distribution'] = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # App distribution
        cursor.execute("""
            SELECT app_name, COUNT(*) as count
            FROM test_cases 
            WHERE is_active = 1 AND app_name IS NOT NULL AND app_name != ''
            GROUP BY app_name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['app_distribution'] = {row['app_name']: row['count'] for row in cursor.fetchall()}
        
        # Feature distribution
        cursor.execute("""
            SELECT feature, COUNT(*) as count
            FROM test_cases 
            WHERE is_active = 1 AND feature IS NOT NULL AND feature != ''
            GROUP BY feature
            ORDER BY count DESC
            LIMIT 20
        """)
        stats['feature_distribution'] = {row['feature']: row['count'] for row in cursor.fetchall()}
        
        return stats

    def optimize_database(self):
        """Run database optimization tasks"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        print("Running database optimization...")
        
        try:
            # Vacuum database
            cursor.execute("VACUUM")
            
            # Analyze for query optimization
            cursor.execute("ANALYZE")
            
            # Update statistics
            cursor.execute("PRAGMA optimize")
            
            connection.commit()
            print("Database optimization completed")
            
        except Exception as e:
            print(f"Database optimization failed: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._close_connection()
