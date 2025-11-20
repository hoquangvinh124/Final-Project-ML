-- Admin Schema
-- Version: 2.0 - Refactored
-- Date: 2025-11-19
-- Changes:
--   - Removed admin_activity_log table (not needed)

-- Admin Users Table (separate from customer users for security)
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'admin', 'manager', 'staff') DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- Insert default admin account (password: admin123)
-- Password hash for 'admin123' using SHA-256
INSERT INTO admin_users (username, email, password_hash, full_name, role)
VALUES ('admin', 'admin@coffeeshop.com',
        SHA2('admin123', 256),
        'System Administrator', 'super_admin')
ON DUPLICATE KEY UPDATE username=username;
