"""
Database service for Test Case Management System
"""

import sqlite3
import os
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.utils.path_resolver import path_resolver
from datetime import datetime
from app.models.test_case import TestCase
from app.models.file_metadata import FileMetadata
from app.models.sync_status import SyncStatus

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(path_resolver.get_database_path())
        self._local = threading.local()
        self._ensure_data_directory()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _close_connection(self):
        """Close thread-local database connection"""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._close_connection()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        try:
            data_dir = Path(self.db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            print(f"Data directory ensured: {data_dir}")
        except Exception as e:
            print(f"Error creating data directory: {e}")
            raise

    def initialize(self):
        """Initialize database connection and create tables"""
        try:
            self._ensure_data_directory()
            
            connection = self._get_connection()
            
            self.create_tables()
            self.migrate_schema()
            self.create_indexes()
            
            print(f"Database initialized successfully: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            try:
                self._create_basic_database()
                print("Basic database created as fallback")
                return True
            except Exception as fallback_error:
                print(f"Fallback database creation failed: {fallback_error}")
                print("Continuing without database - app will work with limited functionality")
                return False

    def _create_basic_database(self):
        """Create a basic database file with minimal structure"""
        try:
            self._ensure_data_directory()
            
            connection = self._get_connection()
            
            cursor = connection.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tc_id TEXT,
                    summary TEXT,
                    feature TEXT,
                    priority TEXT,
                    status TEXT,
                    app_name TEXT,
                    test_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT,
                    file_size INTEGER,
                    last_modified TIMESTAMP,
                    last_synced TIMESTAMP,
                    sync_status TEXT DEFAULT 'pending',
                    remote_url TEXT,
                    remote_hash TEXT,
                    remote_version TEXT,
                    local_path TEXT,
                    local_hash TEXT,
                    local_version TEXT,
                    record_count INTEGER,
                    processing_time REAL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_id TEXT UNIQUE NOT NULL,
                    strategy TEXT,
                    status TEXT,
                    total_files INTEGER DEFAULT 0,
                    processed_files INTEGER DEFAULT 0,
                    failed_files INTEGER DEFAULT 0,
                    total_test_cases INTEGER DEFAULT 0,
                    processed_test_cases INTEGER DEFAULT 0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration REAL,
                    apps TEXT,
                    test_types TEXT,
                    priority_files TEXT,
                    success BOOLEAN DEFAULT FALSE,
                    error_message TEXT,
                    warnings TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            connection.commit()
            print("Basic database structure created")
            
        except Exception as e:
            print(f"Error creating basic database: {e}")
            raise
    
    def create_tables(self):
        """Create database tables"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_id TEXT NOT NULL,
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                file_size INTEGER,
                last_modified TIMESTAMP,
                last_synced TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                remote_url TEXT,
                remote_hash TEXT,
                remote_version TEXT,
                local_path TEXT,
                local_hash TEXT,
                local_version TEXT,
                record_count INTEGER,
                processing_time REAL,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_id TEXT UNIQUE NOT NULL,
                strategy TEXT,
                status TEXT,
                total_files INTEGER DEFAULT 0,
                processed_files INTEGER DEFAULT 0,
                failed_files INTEGER DEFAULT 0,
                total_test_cases INTEGER DEFAULT 0,
                processed_test_cases INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration REAL,
                apps TEXT,
                test_types TEXT,
                priority_files TEXT,
                success BOOLEAN DEFAULT FALSE,
                error_message TEXT,
                warnings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        connection.commit()
    
    def migrate_schema(self):
        """Migrate database schema to add missing columns"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            cursor.execute("PRAGMA table_info(test_cases)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'file_id' not in columns:
                print("[INFO] Adding file_id column to test_cases table...")
                cursor.execute("ALTER TABLE test_cases ADD COLUMN file_id TEXT")
                print("[OK] file_id column added")
            
            if 'local_version' not in columns:
                print("[INFO] Adding local_version column to test_cases table...")
                cursor.execute("ALTER TABLE test_cases ADD COLUMN local_version TEXT")
                print("[OK] local_version column added")
            
            missing_columns = [
                ('screen_id', 'TEXT'),
                ('expected_behavior', 'TEXT'),
                ('procedure', 'TEXT'),
                ('preconditions', 'TEXT'),
                ('test_category', 'TEXT')
            ]
            
            for column_name, column_type in missing_columns:
                if column_name not in columns:
                    print(f"[INFO] Adding {column_name} column to test_cases table...")
                    cursor.execute(f"ALTER TABLE test_cases ADD COLUMN {column_name} {column_type}")
                    print(f"[OK] {column_name} column added")
            
            connection.commit()
            print("[OK] Database schema migration completed")
            
        except Exception as e:
            print(f"[WARN] Schema migration warning: {e}")
            pass
    
    def create_indexes(self):
        """Create database indexes"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_directory ON test_cases(directory_structure)')
        
        try:
            cursor.execute("PRAGMA table_info(test_cases)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'file_id' in columns:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id)')
            else:
                print("[INFO] file_id column not found, skipping index creation")
        except Exception as e:
            print(f"Warning: Could not create file_id index: {e}")
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_file_id ON file_metadata(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_sync_status ON file_metadata(sync_status)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status_id ON sync_status(sync_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status_status ON sync_status(status)')
        
        connection.commit()
    
    def search_test_cases(self, filters: Dict[str, Any] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search test cases with filters and pagination"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        where_conditions = []
        params = []
        
        if filters:
            for key, value in filters.items():
                if value and key in ['tc_id', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure']:
                    where_conditions.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        cursor.execute(f"SELECT COUNT(*) FROM test_cases WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        query = f"""
            SELECT tc_id, summary, feature, priority, status, screen_id, test_type,
                   expected_behavior, procedure, preconditions, file_path, 
                   directory_structure, app_name, test_category, file_id, local_version
            FROM test_cases 
            WHERE {where_clause}
            ORDER BY tc_id
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return {
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM test_cases")
        stats['total_cases'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM test_cases GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT priority, COUNT(*) FROM test_cases GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT feature, COUNT(*) FROM test_cases GROUP BY feature")
        stats['by_feature'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT app_name, COUNT(*) FROM test_cases GROUP BY app_name")
        stats['by_app'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT test_type, COUNT(*) FROM test_cases GROUP BY test_type")
        stats['by_test_type'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT directory_structure, COUNT(*) FROM test_cases GROUP BY directory_structure")
        stats['by_directory'] = dict(cursor.fetchall())
        
        return stats
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get unique values for filter dropdowns"""
        connection = self._get_connection()
        cursor = connection.cursor()
        
        options = {}
        
        columns = ['feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure']
        
        for column in columns:
            cursor.execute(f"SELECT DISTINCT {column} FROM test_cases WHERE {column} IS NOT NULL ORDER BY {column}")
            options[column] = [row[0] for row in cursor.fetchall()]
        
        return options
    
    def insert_test_case(self, test_case: TestCase) -> bool:
        """Insert a test case"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO test_cases 
                (tc_id, summary, feature, priority, status, screen_id, test_type,
                 expected_behavior, procedure, preconditions, file_path, 
                 directory_structure, app_name, test_category, file_id, local_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_case.tc_id, test_case.summary, test_case.feature, test_case.priority,
                test_case.status, test_case.screen_id, test_case.test_type,
                test_case.expected_behavior, test_case.procedure, test_case.preconditions,
                test_case.file_path, test_case.directory_structure, test_case.app_name,
                test_case.test_category, test_case.file_id, test_case.local_version
            ))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting test case: {e}")
            return False
    
    def update_file_metadata(self, file_metadata: FileMetadata) -> bool:
        """Update file metadata"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO file_metadata 
                (file_id, file_path, file_hash, file_size, last_modified, last_synced,
                 sync_status, remote_url, remote_hash, remote_version, local_path,
                 local_hash, local_version, record_count, processing_time, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_metadata.file_id, file_metadata.file_path, file_metadata.file_hash,
                file_metadata.file_size, file_metadata.last_modified, file_metadata.last_synced,
                file_metadata.sync_status, file_metadata.remote_url, file_metadata.remote_hash,
                file_metadata.remote_version, file_metadata.local_path, file_metadata.local_hash,
                file_metadata.local_version, file_metadata.record_count, file_metadata.processing_time,
                file_metadata.error_message
            ))
            connection.commit()
            return True
        except Exception as e:
            print(f"Error updating file metadata: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if database is properly initialized"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_cases'")
            result = cursor.fetchone()
            return result is not None
            
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

    def get_connection_status(self) -> Dict[str, Any]:
        """Get database connection status information"""
        try:
            if not self.is_initialized():
                return {
                    'connected': False,
                    'error': 'No database connection',
                    'path': self.db_path,
                    'exists': os.path.exists(self.db_path)
                }
            
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            return {
                'connected': True,
                'path': self.db_path,
                'exists': os.path.exists(self.db_path),
                'table_count': table_count,
                'tables': self._get_table_names()
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'path': self.db_path,
                'exists': os.path.exists(self.db_path)
            }

    def _get_table_names(self) -> List[str]:
        """Get list of table names in the database"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def safe_execute(self, query, params=None):
        """Safely execute a database query with error handling"""
        try:
            if not self.is_initialized():
                return None, "Database not available"
            
            connection = self._get_connection()
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall(), None
            
        except Exception as e:
            return None, str(e)

    def safe_insert(self, query, params):
        """Safely insert data with error handling"""
        try:
            if not self.is_initialized():
                return False, "Database not available"
            
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return True, None
            
        except Exception as e:
            return False, str(e)

    def get_safe_statistics(self):
        """Get statistics safely, returning empty data if database is not available"""
        try:
            if not self.is_initialized():
                return {
                    'total_cases': 0,
                    'by_status': {},
                    'by_priority': {},
                    'by_feature': {},
                    'by_app': {},
                    'by_test_type': {},
                    'by_directory': {}
                }
            
            return self.get_statistics()
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_cases': 0,
                'by_status': {},
                'by_priority': {},
                'by_feature': {},
                'by_app': {},
                'by_test_type': {},
                'by_directory': {}
            }

    def get_safe_filter_options(self):
        """Get filter options safely, returning empty data if database is not available"""
        try:
            if not self.is_initialized():
                return {
                    'feature': [],
                    'status': [],
                    'priority': [],
                    'app_name': [],
                    'test_type': [],
                    'directory_structure': []
                }
            
            return self.get_filter_options()
            
        except Exception as e:
            print(f"Error getting filter options: {e}")
            return {
                'feature': [],
                'status': [],
                'priority': [],
                'app_name': [],
                'test_type': [],
                'directory_structure': []
            }

    def close(self):
        """Close database connection"""
        self._close_connection()
