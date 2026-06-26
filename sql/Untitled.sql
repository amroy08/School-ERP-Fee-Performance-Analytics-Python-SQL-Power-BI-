CREATE DATABASE school_erp_analytics;

USE school_erp_analytics;

CREATE TABLE fees_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    sr_no INT,
    student_name VARCHAR(150),
    school_type VARCHAR(50),
    class VARCHAR(20),
    grade INT,
    section VARCHAR(10),
    contact VARCHAR(30),
    fees DECIMAL(12,2),
    old_balance DECIMAL(12,2),
    total DECIMAL(12,2),
    received DECIMAL(12,2),
    outstanding DECIMAL(12,2),
    erp_status VARCHAR(50),
    payment_status VARCHAR(50),
    last_paid_month VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

USE school_erp_analytics;

SELECT COUNT(*) AS total_rows
FROM fees_data;

