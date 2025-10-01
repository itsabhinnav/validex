"""
Database service for Test Case Management System
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.models.test_case import TestCase
from app.models.file_metadata import FileMetadata
from app.models.sync_status import SyncStatus

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_path: str = "data/test_cases.db"):
        self.db_path = db_path
        self.connection = None
    
    def initialize(self):
        """Initialize database connection and create tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.create_tables()
            self.create_indexes()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Continue without database for now
            pass
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Test cases table
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
        
        # File metadata table
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
        
        # Sync status table
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
        
        self.connection.commit()
    
    def create_indexes(self):
        """Create database indexes"""
        cursor = self.connection.cursor()
        
        # Test cases indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_directory ON test_cases(directory_structure)')
        
        # Check if file_id column exists before creating index
        try:
            cursor.execute("PRAGMA table_info(test_cases)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'file_id' in columns:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id)')
        except Exception as e:
            print(f"Warning: Could not create file_id index: {e}")
        
        # File metadata indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_file_id ON file_metadata(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_sync_status ON file_metadata(sync_status)')
        
        # Sync status indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status_id ON sync_status(sync_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status_status ON sync_status(status)')
        
        self.connection.commit()
    
    def search_test_cases(self, filters: Dict[str, Any] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search test cases with filters and pagination"""
        cursor = self.connection.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if filters:
            for key, value in filters.items():
                if value and key in ['tc_id', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure']:
                    where_conditions.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM test_cases WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
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
        cursor = self.connection.cursor()
        
        stats = {}
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM test_cases")
        stats['total_cases'] = cursor.fetchone()[0]
        
        # By status
        cursor.execute("SELECT status, COUNT(*) FROM test_cases GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())
        
        # By priority
        cursor.execute("SELECT priority, COUNT(*) FROM test_cases GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        # By feature
        cursor.execute("SELECT feature, COUNT(*) FROM test_cases GROUP BY feature")
        stats['by_feature'] = dict(cursor.fetchall())
        
        # By app
        cursor.execute("SELECT app_name, COUNT(*) FROM test_cases GROUP BY app_name")
        stats['by_app'] = dict(cursor.fetchall())
        
        # By test type
        cursor.execute("SELECT test_type, COUNT(*) FROM test_cases GROUP BY test_type")
        stats['by_test_type'] = dict(cursor.fetchall())
        
        # By directory
        cursor.execute("SELECT directory_structure, COUNT(*) FROM test_cases GROUP BY directory_structure")
        stats['by_directory'] = dict(cursor.fetchall())
        
        return stats
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get unique values for filter dropdowns"""
        cursor = self.connection.cursor()
        
        options = {}
        
        # Get unique values for each filterable column
        columns = ['feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure']
        
        for column in columns:
            cursor.execute(f"SELECT DISTINCT {column} FROM test_cases WHERE {column} IS NOT NULL ORDER BY {column}")
            options[column] = [row[0] for row in cursor.fetchall()]
        
        return options
    
    def insert_test_case(self, test_case: TestCase) -> bool:
        """Insert a test case"""
        try:
            cursor = self.connection.cursor()
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
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting test case: {e}")
            return False
    
    def update_file_metadata(self, file_metadata: FileMetadata) -> bool:
        """Update file metadata"""
        try:
            cursor = self.connection.cursor()
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
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating file metadata: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
