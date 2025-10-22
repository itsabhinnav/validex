"""
High-Performance Database Migration Service
Handles database schema migrations and data transformations
"""

import sqlite3
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class DatabaseMigrationService:
    """Service for managing database migrations and schema updates"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.migrations_dir = Path(__file__).parent.parent.parent / 'migrations'
        self.migrations_dir.mkdir(exist_ok=True)
        
    def create_migration_table(self):
        """Create migrations tracking table"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time REAL,
                success BOOLEAN DEFAULT 1
            )
        ''')
        
        connection.commit()
        connection.close()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY applied_at")
        migrations = [row[0] for row in cursor.fetchall()]
        
        connection.close()
        return migrations
    
    def apply_migration(self, migration_name: str, migration_sql: str) -> bool:
        """Apply a single migration"""
        start_time = time.time()
        
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            
            # Execute migration
            cursor.executescript(migration_sql)
            
            # Record migration
            execution_time = time.time() - start_time
            cursor.execute('''
                INSERT INTO schema_migrations (migration_name, execution_time, success)
                VALUES (?, ?, 1)
            ''', (migration_name, execution_time))
            
            connection.commit()
            connection.close()
            
            self.logger.info(f"Migration {migration_name} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration {migration_name} failed: {e}")
            
            # Record failed migration
            try:
                connection = sqlite3.connect(self.db_path)
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO schema_migrations (migration_name, execution_time, success)
                    VALUES (?, ?, 0)
                ''', (migration_name, time.time() - start_time))
                connection.commit()
                connection.close()
            except:
                pass
            
            return False
    
    def migrate_to_high_performance_schema(self) -> bool:
        """Migrate from old schema to high-performance schema"""
        migration_name = "migrate_to_high_performance_schema"
        
        # Check if already applied
        if migration_name in self.get_applied_migrations():
            self.logger.info("High-performance schema migration already applied")
            return True
        
        migration_sql = '''
        -- Create backup of existing data
        CREATE TABLE IF NOT EXISTS test_cases_backup AS SELECT * FROM test_cases;
        
        -- Drop old indexes
        DROP INDEX IF EXISTS idx_tc_id;
        DROP INDEX IF EXISTS idx_feature;
        DROP INDEX IF EXISTS idx_priority;
        DROP INDEX IF EXISTS idx_status;
        
        -- Create new optimized tables
        CREATE TABLE IF NOT EXISTS test_cases_new (
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
        );
        
        -- Migrate existing data
        INSERT INTO test_cases_new (
            tc_id, summary, feature, priority, status, screen_id, test_type,
            expected_behavior, procedure, preconditions, file_path, directory_structure,
            app_name, test_category, file_id, local_version, created_at, updated_at
        )
        SELECT 
            tc_id, summary, feature, priority, status, screen_id, test_type,
            expected_behavior, procedure, preconditions, file_path, directory_structure,
            app_name, test_category, file_id, local_version, created_at, updated_at
        FROM test_cases;
        
        -- Drop old table and rename new one
        DROP TABLE test_cases;
        ALTER TABLE test_cases_new RENAME TO test_cases;
        
        -- Create performance indexes
        CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id);
        CREATE INDEX IF NOT EXISTS idx_tc_id_active ON test_cases(tc_id, is_active);
        CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature);
        CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority);
        CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status);
        CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name);
        CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type);
        CREATE INDEX IF NOT EXISTS idx_screen_id ON test_cases(screen_id);
        CREATE INDEX IF NOT EXISTS idx_feature_priority ON test_cases(feature, priority);
        CREATE INDEX IF NOT EXISTS idx_app_status ON test_cases(app_name, status);
        CREATE INDEX IF NOT EXISTS idx_feature_status ON test_cases(feature, status);
        CREATE INDEX IF NOT EXISTS idx_priority_status ON test_cases(priority, status);
        CREATE INDEX IF NOT EXISTS idx_file_path ON test_cases(file_path);
        CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id);
        CREATE INDEX IF NOT EXISTS idx_created_at ON test_cases(created_at);
        CREATE INDEX IF NOT EXISTS idx_updated_at ON test_cases(updated_at);
        
        -- Create search index table
        CREATE TABLE IF NOT EXISTS test_case_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tc_id TEXT NOT NULL,
            searchable_text TEXT,
            feature_normalized TEXT,
            priority_normalized TEXT,
            status_normalized TEXT,
            app_normalized TEXT,
            test_type_normalized TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Populate search index
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
        WHERE is_active = 1;
        
        -- Create indexes for search table
        CREATE INDEX IF NOT EXISTS idx_index_tc_id ON test_case_index(tc_id);
        CREATE INDEX IF NOT EXISTS idx_searchable_text ON test_case_index(searchable_text);
        CREATE INDEX IF NOT EXISTS idx_feature_norm ON test_case_index(feature_normalized);
        CREATE INDEX IF NOT EXISTS idx_priority_norm ON test_case_index(priority_normalized);
        CREATE INDEX IF NOT EXISTS idx_status_norm ON test_case_index(status_normalized);
        CREATE INDEX IF NOT EXISTS idx_app_norm ON test_case_index(app_normalized);
        CREATE INDEX IF NOT EXISTS idx_test_type_norm ON test_case_index(test_type_normalized);
        
        -- Optimize database
        ANALYZE;
        VACUUM;
        '''
        
        return self.apply_migration(migration_name, migration_sql)
    
    def create_initial_schema(self) -> bool:
        """Create initial high-performance schema"""
        migration_name = "create_initial_high_performance_schema"
        
        # Check if already applied
        if migration_name in self.get_applied_migrations():
            self.logger.info("Initial high-performance schema already created")
            return True
        
        migration_sql = '''
        -- Create optimized test_cases table
        CREATE TABLE IF NOT EXISTS test_cases (
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
        );
        
        -- Create file metadata table
        CREATE TABLE IF NOT EXISTS file_metadata (
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
        );
        
        -- Create search cache table
        CREATE TABLE IF NOT EXISTS search_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_key TEXT UNIQUE NOT NULL,
            cache_data TEXT NOT NULL,
            cache_type TEXT NOT NULL,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create test case index table
        CREATE TABLE IF NOT EXISTS test_case_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tc_id TEXT NOT NULL,
            searchable_text TEXT,
            feature_normalized TEXT,
            priority_normalized TEXT,
            status_normalized TEXT,
            app_normalized TEXT,
            test_type_normalized TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create performance indexes
        CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id);
        CREATE INDEX IF NOT EXISTS idx_tc_id_active ON test_cases(tc_id, is_active);
        CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature);
        CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority);
        CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status);
        CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name);
        CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type);
        CREATE INDEX IF NOT EXISTS idx_screen_id ON test_cases(screen_id);
        CREATE INDEX IF NOT EXISTS idx_feature_priority ON test_cases(feature, priority);
        CREATE INDEX IF NOT EXISTS idx_app_status ON test_cases(app_name, status);
        CREATE INDEX IF NOT EXISTS idx_feature_status ON test_cases(feature, status);
        CREATE INDEX IF NOT EXISTS idx_priority_status ON test_cases(priority, status);
        CREATE INDEX IF NOT EXISTS idx_file_path ON test_cases(file_path);
        CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id);
        CREATE INDEX IF NOT EXISTS idx_created_at ON test_cases(created_at);
        CREATE INDEX IF NOT EXISTS idx_updated_at ON test_cases(updated_at);
        
        -- File metadata indexes
        CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(file_path);
        CREATE INDEX IF NOT EXISTS idx_file_metadata_hash ON file_metadata(file_hash);
        CREATE INDEX IF NOT EXISTS idx_file_metadata_status ON file_metadata(sync_status);
        
        -- Search cache indexes
        CREATE INDEX IF NOT EXISTS idx_cache_key ON search_cache(cache_key);
        CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_at);
        
        -- Test case index table indexes
        CREATE INDEX IF NOT EXISTS idx_index_tc_id ON test_case_index(tc_id);
        CREATE INDEX IF NOT EXISTS idx_searchable_text ON test_case_index(searchable_text);
        CREATE INDEX IF NOT EXISTS idx_feature_norm ON test_case_index(feature_normalized);
        CREATE INDEX IF NOT EXISTS idx_priority_norm ON test_case_index(priority_normalized);
        CREATE INDEX IF NOT EXISTS idx_status_norm ON test_case_index(status_normalized);
        CREATE INDEX IF NOT EXISTS idx_app_norm ON test_case_index(app_normalized);
        CREATE INDEX IF NOT EXISTS idx_test_type_norm ON test_case_index(test_type_normalized);
        
        -- Optimize database
        ANALYZE;
        '''
        
        return self.apply_migration(migration_name, migration_sql)
    
    def run_all_migrations(self) -> Dict[str, Any]:
        """Run all pending migrations"""
        self.create_migration_table()
        
        migrations_to_run = [
            ("create_initial_high_performance_schema", self.create_initial_schema),
            ("migrate_to_high_performance_schema", self.migrate_to_high_performance_schema)
        ]
        
        results = {
            'success': True,
            'migrations_applied': [],
            'migrations_failed': [],
            'total_time': 0
        }
        
        start_time = time.time()
        
        for migration_name, migration_func in migrations_to_run:
            try:
                if migration_func():
                    results['migrations_applied'].append(migration_name)
                else:
                    results['migrations_failed'].append(migration_name)
                    results['success'] = False
            except Exception as e:
                self.logger.error(f"Migration {migration_name} failed: {e}")
                results['migrations_failed'].append(migration_name)
                results['success'] = False
        
        results['total_time'] = time.time() - start_time
        
        return results
