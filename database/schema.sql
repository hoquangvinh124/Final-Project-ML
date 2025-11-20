-- Coffee Shop Database Schema
-- Version: 2.0 - Refactored
-- Date: 2025-11-19
-- Changes:
--   - Removed placeholder tables (otp_codes, badges, loyalty_missions, etc.)
--   - Changed icon_url/image_url to base64 image storage
--   - Removed unused verification fields

CREATE DATABASE IF NOT EXISTS coffee_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE coffee_shop;

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    avatar LONGTEXT,  -- Base64 encoded image (LONGTEXT for large images)
    membership_tier ENUM('Bronze', 'Silver', 'Gold') DEFAULT 'Bronze',
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_membership (membership_tier)
) ENGINE=InnoDB;

-- User Preferences Table
CREATE TABLE user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    favorite_size ENUM('S', 'M', 'L') DEFAULT 'M',
    favorite_sugar_level INT DEFAULT 50,
    favorite_ice_level INT DEFAULT 50,
    preferred_toppings JSON,
    allergies JSON,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- PRODUCTS & CATALOG
-- ============================================

-- Categories Table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    image LONGTEXT,  -- Base64 encoded image (LONGTEXT for large images)
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Products Table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    description TEXT,
    ingredients TEXT,
    allergens JSON,
    image LONGTEXT,  -- Base64 encoded image (LONGTEXT for large images)
    base_price DECIMAL(10, 2) NOT NULL,
    calories_small INT,
    calories_medium INT,
    calories_large INT,
    is_hot BOOLEAN DEFAULT TRUE,
    is_cold BOOLEAN DEFAULT TRUE,
    is_caffeine_free BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    is_bestseller BOOLEAN DEFAULT FALSE,
    is_seasonal BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2) DEFAULT 0,
    total_reviews INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_featured (is_featured),
    INDEX idx_available (is_available)
) ENGINE=InnoDB;

-- Toppings Table
CREATE TABLE toppings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    calories INT DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Product Sizes Table
CREATE TABLE product_sizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size ENUM('S', 'M', 'L') NOT NULL,
    price_adjustment DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_size (product_id, size)
) ENGINE=InnoDB;

-- ============================================
-- SHOPPING & FAVORITES
-- ============================================

-- Favorites Table
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id),
    INDEX idx_user (user_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB;

-- Shopping Cart Table
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    size ENUM('S', 'M', 'L') NOT NULL,
    quantity INT NOT NULL,
    sugar_level INT DEFAULT 50,
    ice_level INT DEFAULT 50,
    temperature ENUM('hot', 'cold') DEFAULT 'cold',
    toppings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- STORES & BRANCHES
-- ============================================

-- Stores/Branches Table
CREATE TABLE stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100),
    district VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    opening_time TIME,
    closing_time TIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- ORDERS
-- ============================================

-- Orders Table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    store_id INT,
    order_type ENUM('pickup', 'delivery', 'dine_in') NOT NULL,
    status ENUM('pending', 'confirmed', 'preparing', 'ready', 'delivering', 'completed', 'cancelled') DEFAULT 'pending',
    subtotal DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    delivery_fee DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('cash', 'momo', 'shopeepay', 'zalopay', 'applepay', 'googlepay', 'card') NOT NULL,
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    delivery_address TEXT,
    delivery_latitude DECIMAL(10, 8),
    delivery_longitude DECIMAL(11, 8),
    table_number VARCHAR(20),
    qr_code VARCHAR(100),
    notes TEXT,
    estimated_ready_time TIMESTAMP,
    completed_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_order_number (order_number)
) ENGINE=InnoDB;

-- Order Items Table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    size ENUM('S', 'M', 'L') NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    sugar_level INT DEFAULT 50,
    ice_level INT DEFAULT 50,
    temperature ENUM('hot', 'cold') DEFAULT 'cold',
    toppings JSON,
    topping_cost DECIMAL(10, 2) DEFAULT 0,
    subtotal DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

-- ============================================
-- VOUCHERS & LOYALTY
-- ============================================

-- Vouchers Table
CREATE TABLE vouchers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type ENUM('percentage', 'fixed') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    min_order_amount DECIMAL(10, 2) DEFAULT 0,
    max_discount_amount DECIMAL(10, 2),
    usage_limit INT,
    usage_per_user INT DEFAULT 1,
    current_usage INT DEFAULT 0,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    applicable_to ENUM('all', 'specific_products', 'specific_categories') DEFAULT 'all',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- User Vouchers (for tracking user-specific voucher usage)
CREATE TABLE user_vouchers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    voucher_id INT NOT NULL,
    times_used INT DEFAULT 0,
    last_used_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (voucher_id) REFERENCES vouchers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_voucher (user_id, voucher_id)
) ENGINE=InnoDB;

-- Voucher Usage History Table
CREATE TABLE voucher_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voucher_id INT NOT NULL,
    user_id INT NOT NULL,
    order_id INT,
    discount_amount DECIMAL(10, 2) NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voucher_id) REFERENCES vouchers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    INDEX idx_voucher (voucher_id),
    INDEX idx_user (user_id),
    INDEX idx_used_at (used_at)
) ENGINE=InnoDB;

-- Loyalty Points History Table
CREATE TABLE loyalty_points_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points INT NOT NULL,
    transaction_type ENUM('earn', 'redeem', 'expire', 'adjust') NOT NULL,
    description VARCHAR(255),
    order_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB;

-- ============================================
-- REVIEWS & RATINGS
-- ============================================

-- Reviews Table
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    service_rating INT CHECK (service_rating >= 1 AND service_rating <= 5),
    images JSON,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB;

-- ============================================
-- NOTIFICATIONS
-- ============================================

-- Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('order_update', 'promotion', 'loyalty', 'system') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_order_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_unread (user_id, is_read)
) ENGINE=InnoDB;

-- ============================================
-- SAMPLE DATA
-- ============================================

-- Insert Sample Categories
INSERT INTO categories (name, name_en, description, display_order) VALUES
('Cà Phê', 'Coffee', 'Các loại cà phê truyền thống và hiện đại', 1),
('Trà', 'Tea', 'Trà sữa và trà trái cây', 2),
('Bánh Ngọt', 'Pastries', 'Bánh ngọt và đồ ăn nhẹ', 3),
('Sinh Tố', 'Smoothies', 'Sinh tố trái cây tươi', 4),
('Đồ Uống Đá Xay', 'Frozen Drinks', 'Các loại đồ uống đá xay', 5);

-- Insert Sample Toppings
INSERT INTO toppings (name, name_en, price, calories) VALUES
('Trân Châu Đen', 'Black Pearl', 10000, 120),
('Trân Châu Trắng', 'White Pearl', 10000, 120),
('Thạch Cà Phê', 'Coffee Jelly', 8000, 80),
('Pudding', 'Pudding', 12000, 150),
('Kem Cheese', 'Cream Cheese', 15000, 180),
('Thạch Dừa', 'Coconut Jelly', 8000, 70);

-- Insert Sample Stores
INSERT INTO stores (name, address, city, district, phone, opening_time, closing_time) VALUES
('Highland Coffee Nguyễn Huệ', '123 Nguyễn Huệ, Quận 1', 'Hồ Chí Minh', 'Quận 1', '0281234567', '07:00:00', '23:00:00'),
('Highland Coffee Lê Lợi', '456 Lê Lợi, Quận 1', 'Hồ Chí Minh', 'Quận 1', '0281234568', '07:00:00', '23:00:00'),
('Highland Coffee Võ Văn Tần', '789 Võ Văn Tần, Quận 3', 'Hồ Chí Minh', 'Quận 3', '0281234569', '07:00:00', '23:00:00');

-- Insert Sample Products
INSERT INTO products (category_id, name, name_en, description, base_price, calories_small, calories_medium, calories_large, is_hot, is_cold, is_new, is_bestseller) VALUES
(1, 'Phin Cà Phê Sữa Đá', 'Iced Milk Coffee', 'Cà phê phin truyền thống kết hợp sữa đặc', 45000, 150, 200, 280, TRUE, TRUE, TRUE, TRUE),
(1, 'Bạc Xỉu', 'Bac Xiu', 'Cà phê sữa nhẹ nhàng, ngọt dịu', 45000, 180, 230, 300, TRUE, TRUE, TRUE, FALSE),
(1, 'Americano', 'Americano', 'Cà phê đen pha espresso', 40000, 10, 15, 20, TRUE, TRUE, TRUE, FALSE),
(1, 'Cappuccino', 'Cappuccino', 'Espresso với sữa tươi và foam mịn', 55000, 120, 160, 220, TRUE, TRUE, FALSE, TRUE),
(2, 'Trà Sữa Trân Châu Đường Đen', 'Brown Sugar Milk Tea', 'Trà sữa kết hợp trân châu và đường đen', 55000, 300, 380, 450, FALSE, TRUE, FALSE, TRUE),
(2, 'Trà Đào Cam Sả', 'Peach Passion Fruit Tea', 'Trà trái cây tươi mát', 50000, 120, 180, 240, FALSE, TRUE, FALSE, FALSE),
(3, 'Bánh Croissant Bơ', 'Butter Croissant', 'Bánh sừng bò giòn tan thơm bơ', 35000, 280, NULL, NULL, FALSE, FALSE, FALSE, FALSE),
(3, 'Tiramisu', 'Tiramisu', 'Bánh Tiramisu truyền thống Ý', 50000, 350, NULL, NULL, FALSE, FALSE, FALSE, FALSE);
