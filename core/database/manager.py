import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import hashlib
import json

class DatabaseManager:
    def __init__(self, db_path="data/test_cases.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create test_cases table
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
                file_path TEXT NOT NULL,
                directory_structure TEXT,
                app_name TEXT,
                test_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create file_metadata table for tracking file changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_hash TEXT,
                last_modified TIMESTAMP,
                record_count INTEGER,
                last_processed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for fast searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_directory ON test_cases(directory_structure)')
        
        # Create full-text search index
        cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS test_cases_fts USING fts5(tc_id, summary, feature, expected_behavior, content="test_cases", content_rowid="id")')
        
        conn.commit()
        conn.close()
    
    def get_file_hash(self, file_path):
        """Calculate file hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def is_file_changed(self, file_path):
        """Check if file has been modified since last processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_hash = self.get_file_hash(file_path)
        cursor.execute('SELECT file_hash FROM file_metadata WHERE file_path = ?', (file_path,))
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return True  # File not in database
        
        return result[0] != current_hash
    
    def process_excel_file(self, file_path, base_dir):
        """Process a single Excel file and store in database"""
        try:
            df = pd.read_excel(file_path)
            relative_path = os.path.relpath(file_path, base_dir)
            path_parts = relative_path.split(os.sep)
            
            app_name = path_parts[0] if len(path_parts) > 0 else 'Unknown'
            test_category = path_parts[1] if len(path_parts) > 1 else 'Unknown'
            directory_structure = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove existing records for this file
            cursor.execute('DELETE FROM test_cases WHERE file_path = ?', (relative_path,))
            
            # Insert new records
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO test_cases 
                    (tc_id, summary, feature, priority, status, screen_id, test_type, 
                     expected_behavior, file_path, directory_structure, app_name, test_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('TC ID', ''),
                    row.get('Summary', ''),
                    row.get('Feature', ''),
                    row.get('Priority', ''),
                    row.get('Status', ''),
                    row.get('Screen ID', ''),
                    row.get('type', ''),
                    row.get('Expected Behavior', ''),
                    relative_path,
                    directory_structure,
                    app_name,
                    test_category
                ))
            
            # Update file metadata
            file_hash = self.get_file_hash(file_path)
            record_count = len(df)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            cursor.execute('''
                INSERT OR REPLACE INTO file_metadata 
                (file_path, file_hash, last_modified, record_count, last_processed)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (relative_path, file_hash, last_modified, record_count))
            
            conn.commit()
            conn.close()
            
            return len(df)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return 0
    
    def sync_files(self, base_dir):
        """Sync all Excel files with database (incremental)"""
        total_processed = 0
        total_files = 0
        
        for root, dirs, files in os.walk(base_dir):
            for filename in files:
                if filename.endswith(('.xlsx', '.xls')):
                    file_path = os.path.join(root, filename)
                    total_files += 1
                    
                    if self.is_file_changed(file_path):
                        print(f"Processing {file_path}...")
                        count = self.process_excel_file(file_path, base_dir)
                        total_processed += count
                        print(f"  -> {count} test cases processed")
                    else:
                        print(f"Skipping {file_path} (no changes)")
        
        print(f"Sync complete: {total_processed} test cases from {total_files} files")
        return total_processed
    
    def search_test_cases(self, filters=None, limit=100, offset=0):
        """Search test cases with filters and pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if filters:
            if filters.get('tc_id'):
                where_conditions.append("tc_id LIKE ?")
                params.append(f"%{filters['tc_id']}%")
            
            if filters.get('feature'):
                where_conditions.append("feature LIKE ?")
                params.append(f"%{filters['feature']}%")
            
            if filters.get('status'):
                where_conditions.append("status = ?")
                params.append(filters['status'])
            
            if filters.get('priority'):
                where_conditions.append("priority = ?")
                params.append(filters['priority'])
            
            if filters.get('app_name'):
                where_conditions.append("app_name = ?")
                params.append(filters['app_name'])
            
            if filters.get('test_type'):
                where_conditions.append("test_type = ?")
                params.append(filters['test_type'])
            
            if filters.get('directory_structure'):
                where_conditions.append("directory_structure = ?")
                params.append(filters['directory_structure'])
            
            if filters.get('search_term'):
                # Use FTS for full-text search
                where_conditions.append("id IN (SELECT rowid FROM test_cases_fts WHERE test_cases_fts MATCH ?)")
                params.append(filters['search_term'])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM test_cases WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        query = f"""
            SELECT tc_id, summary, feature, priority, status, screen_id, test_type, 
                   expected_behavior, file_path, directory_structure, app_name, test_category
            FROM test_cases 
            WHERE {where_clause}
            ORDER BY tc_id
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        return {
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }
    
    def get_statistics(self):
        """Get aggregated statistics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        conn.close()
        return stats
    
    def get_filter_options(self):
        """Get unique values for filter dropdowns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        options = {}
        
        # Get unique values for each filterable column
        columns = ['feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure']
        
        for column in columns:
            cursor.execute(f"SELECT DISTINCT {column} FROM test_cases WHERE {column} IS NOT NULL ORDER BY {column}")
            options[column] = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return options

# Global database manager instance
db_manager = DatabaseManager()
