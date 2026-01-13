CREATE DATABASE school_erp_analysis;
GO

USE school_erp_analysis;
GO

CREATE TABLE staging_erp (
    student_id VARCHAR(20),
    grade VARCHAR(10),
    class VARCHAR(20),
    contact VARCHAR(20),
    contact_valid VARCHAR(10),
    fees DECIMAL(12,2),
    old_balance DECIMAL(12,2),
    total DECIMAL(12,2),
    received DECIMAL(12,2),
    outstanding DECIMAL(12,2),
    payment_status VARCHAR(20),
    outstanding_bucket VARCHAR(20),
    last_paid_month VARCHAR(20),
    school_section VARCHAR(20)
);

CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    grade VARCHAR(10),
    class VARCHAR(20),
    contact VARCHAR(20),
    contact_valid VARCHAR(10),
    school_section VARCHAR(20)
);

CREATE TABLE fee_transactions (
    txn_id INT IDENTITY(1,1) PRIMARY KEY,
    student_id VARCHAR(20),
    fees DECIMAL(12,2),
    old_balance DECIMAL(12,2),
    total DECIMAL(12,2),
    received DECIMAL(12,2),
    outstanding DECIMAL(12,2),
    payment_status VARCHAR(20),
    outstanding_bucket VARCHAR(20),
    last_paid_month VARCHAR(20),
    record_date DATE,
    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);

USE school_erp_analysis;
GO

SELECT TOP 10 * FROM staging_erp;
SELECT COUNT(*) AS rows_in_staging FROM staging_erp;

SELECT DB_NAME() AS current_database;
GO

USE school_erp_analysis;
GO

SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;


USE school_erp_analysis;
GO

SELECT TOP 10 * FROM dbo.clean_erp_fees;
SELECT COUNT(*) AS rows_in_staging FROM dbo.clean_erp_fees;
GO

CREATE TABLE dbo.students (
    student_id NVARCHAR(50) PRIMARY KEY,
    grade NVARCHAR(50),
    class NVARCHAR(50),
    contact NVARCHAR(50),
    contact_valid NVARCHAR(50),
    school_section NVARCHAR(50)
);
GO

CREATE TABLE dbo.fee_transactions (
    txn_id INT IDENTITY(1,1) PRIMARY KEY,
    student_id NVARCHAR(50),
    fees DECIMAL(18,10),
    old_balance DECIMAL(18,10),
    total DECIMAL(18,10),
    received DECIMAL(18,10),
    outstanding DECIMAL(18,10),
    payment_status NVARCHAR(50),
    outstanding_bucket NVARCHAR(50),
    last_paid_month NVARCHAR(50),
    record_date DATE,
    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES dbo.students(student_id)
);
GO

INSERT INTO dbo.students
(student_id, grade, class, contact, contact_valid, school_section)
SELECT DISTINCT
    student_id,
    grade,
    class,
    contact,
    contact_valid,
    school_section
FROM dbo.clean_erp_fees
WHERE student_id IS NOT NULL
  AND LTRIM(RTRIM(student_id)) <> '';
GO

INSERT INTO dbo.fee_transactions
(student_id, fees, old_balance, total, received, outstanding,
 payment_status, outstanding_bucket, last_paid_month, record_date)
SELECT
    student_id,
    fees,
    old_balance,
    total,
    received,
    outstanding,
    payment_status,
    outstanding_bucket,
    last_paid_month,
    CAST(GETDATE() AS DATE)
FROM dbo.clean_erp_fees
WHERE student_id IS NOT NULL
  AND LTRIM(RTRIM(student_id)) <> '';
GO


SELECT COUNT(*) AS students_count FROM dbo.students;
SELECT COUNT(*) AS transactions_count FROM dbo.fee_transactions;
GO

SELECT TOP 20
    student_id,
    total,
    received,
    outstanding,
    (total - (received + outstanding)) AS difference
FROM dbo.fee_transactions
WHERE ABS(total - (received + outstanding)) > 1
ORDER BY difference DESC;
GO

ALTER TABLE dbo.fee_transactions ALTER COLUMN fees DECIMAL(12,2);
ALTER TABLE dbo.fee_transactions ALTER COLUMN old_balance DECIMAL(12,2);
ALTER TABLE dbo.fee_transactions ALTER COLUMN total DECIMAL(12,2);
ALTER TABLE dbo.fee_transactions ALTER COLUMN received DECIMAL(12,2);
ALTER TABLE dbo.fee_transactions ALTER COLUMN outstanding DECIMAL(12,2);
GO

SELECT
    SUM(total) AS total_fee,
    SUM(received) AS total_received,
    SUM(outstanding) AS total_outstanding,
    ROUND(SUM(received) * 100.0 / NULLIF(SUM(total), 0), 2) AS collection_percentage
FROM dbo.fee_transactions;

SELECT TOP 20
    s.student_id,
    s.grade,
    s.class,
    f.outstanding,
    f.last_paid_month
FROM dbo.students s
JOIN dbo.fee_transactions f
    ON s.student_id = f.student_id
WHERE f.outstanding > 0
ORDER BY f.outstanding DESC;


SELECT TOP 20
    s.student_id,
    s.grade,
    s.class,
    f.outstanding,
    f.last_paid_month
FROM dbo.students s
JOIN dbo.fee_transactions f
    ON s.student_id = f.student_id
WHERE f.outstanding >= 15000
  AND (f.last_paid_month IS NULL OR LTRIM(RTRIM(f.last_paid_month)) = '')
ORDER BY f.outstanding DESC;


SELECT
    last_paid_month,
    SUM(received) AS total_received
FROM dbo.fee_transactions
WHERE last_paid_month IS NOT NULL
GROUP BY last_paid_month
ORDER BY total_received DESC;


SELECT
    s.grade,
    SUM(CASE WHEN f.outstanding = 0 THEN 1 ELSE 0 END) AS completed_students,
    SUM(CASE WHEN f.outstanding > 0 THEN 1 ELSE 0 END) AS pending_students
FROM dbo.students s
JOIN dbo.fee_transactions f
    ON s.student_id = f.student_id
GROUP BY s.grade
ORDER BY s.grade;

SELECT
    COUNT(*) AS total_students,
    SUM(CASE WHEN contact IS NULL OR LTRIM(RTRIM(contact)) = '' THEN 1 ELSE 0 END) AS missing_contact,
    SUM(CASE WHEN contact_valid = 'No' THEN 1 ELSE 0 END) AS invalid_contact
FROM dbo.students;

SELECT
    s.school_section,
    SUM(f.total) AS total_fee,
    SUM(f.received) AS received_fee,
    ROUND(SUM(f.received)*100.0 / NULLIF(SUM(f.total),0),2) AS collection_pct
FROM dbo.students s
JOIN dbo.fee_transactions f
    ON s.student_id = f.student_id
GROUP BY s.school_section;



