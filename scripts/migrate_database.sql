-- Migration script for SmartCrop database
-- Run this script to add new tables and columns

-- ============================================================================
-- Add new columns to User table
-- ============================================================================
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS first_name VARCHAR(50);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_name VARCHAR(50);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS location VARCHAR(50);

-- ============================================================================
-- Create Notification table
-- ============================================================================
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
);

-- Create index for faster notification queries
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);

-- ============================================================================
-- Create LoginAttempt table for security
-- ============================================================================
CREATE TABLE IF NOT EXISTS login_attempt (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(50) NOT NULL,
    username VARCHAR(80),
    success BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_login_attempt_ip ON login_attempt(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempt_created_at ON login_attempt(created_at);

-- ============================================================================
-- Verify migration success
-- ============================================================================
SELECT 'Migration completed successfully!' as status;
