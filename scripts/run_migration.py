# -*- coding: utf-8 -*-
"""
Database migration script for SmartCrop
Adds new columns and tables for enhanced features
"""

import psycopg2
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Database connection settings from .env
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'smartcrop'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

def run_migration():
    """Execute database migrations"""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('UTF8')
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Connected to database successfully!")
        print("-" * 50)
        
        # Add new columns to User table
        print("\n1. Adding new columns to User table...")
        
        user_columns = [
            ("first_name", "VARCHAR(50)"),
            ("last_name", "VARCHAR(50)"),
            ("phone", "VARCHAR(20)"),
            ("location", "VARCHAR(50)")
        ]
        
        for col_name, col_type in user_columns:
            try:
                cur.execute('ALTER TABLE "user" ADD COLUMN {} {}'.format(col_name, col_type))
                print("   + Added column: {}".format(col_name))
            except psycopg2.errors.DuplicateColumn:
                print("   - Column {} already exists".format(col_name))
                conn.rollback()
                conn = psycopg2.connect(**DB_CONFIG)
                conn.set_client_encoding('UTF8')
                conn.autocommit = True
                cur = conn.cursor()
        
        # Create Notification table
        print("\n2. Creating Notification table...")
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notification (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    title VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(20) DEFAULT 'info',
                    icon VARCHAR(50) DEFAULT 'fa-bell',
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    link VARCHAR(255)
                )
            """)
            print("   + Notification table created/verified")
        except Exception as e:
            print("   ! Error: {}".format(e))
        
        # Create indexes for notifications
        try:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read)")
            print("   + Notification indexes created")
        except Exception as e:
            print("   ! Index error: {}".format(e))
        
        # Create LoginAttempt table
        print("\n3. Creating LoginAttempt table...")
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS login_attempt (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(50) NOT NULL,
                    username VARCHAR(80),
                    success BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("   + LoginAttempt table created/verified")
        except Exception as e:
            print("   ! Error: {}".format(e))
        
        # Create indexes for login attempts
        try:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_login_attempt_ip ON login_attempt(ip_address)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_login_attempt_created_at ON login_attempt(created_at)")
            print("   + LoginAttempt indexes created")
        except Exception as e:
            print("   ! Index error: {}".format(e))
        
        # Verify tables
        print("\n4. Verifying database structure...")
        
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print("   Tables in database: {}".format(', '.join([t[0] for t in tables])))
        
        # Check user columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print("   User table columns: {}".format(', '.join([c[0] for c in columns])))
        
        print("\n" + "=" * 50)
        print("Migration completed successfully!")
        print("=" * 50)
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print("\nDatabase error: {}".format(e))
        return False
    except Exception as e:
        print("\nError: {}".format(e))
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
