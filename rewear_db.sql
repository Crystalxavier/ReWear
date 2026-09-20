-- USE rewear_db;

-- SHOW TABLES;

-- USE rewear_db;

-- SHOW CREATE TABLE users;
-- SHOW CREATE TABLE items;
-- SHOW CREATE TABLE swap_requests;
-- SHOW CREATE TABLE transactions;

-- DESCRIBE users;
-- DESCRIBE items;
-- DESCRIBE swap_requests;
-- DESCRIBE transactions;

-- ============================================
-- ReWear Database
-- ============================================

CREATE DATABASE IF NOT EXISTS rewear_db;

USE rewear_db;


-- ============================================
-- USERS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    points INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- ITEMS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    clothing_type VARCHAR(100),
    size VARCHAR(50),
    condition_type VARCHAR(100),
    tags VARCHAR(255),
    image VARCHAR(255),
    points INT DEFAULT 50,
    status VARCHAR(50) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ============================================
-- SWAP REQUESTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS swap_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    requester_id INT NOT NULL,
    owner_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (item_id)
        REFERENCES items(id)
        ON DELETE CASCADE,

    FOREIGN KEY (requester_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (owner_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ============================================
-- TRANSACTIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    points INT NOT NULL,
    transaction_type VARCHAR(50),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (item_id)
        REFERENCES items(id)
        ON DELETE CASCADE
);