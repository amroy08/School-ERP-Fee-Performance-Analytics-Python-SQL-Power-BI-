# 📊 School ERP Fee Performance Analytics

An end-to-end **Data Analytics** project built using **Python, MySQL, SQL, Excel, and Power BI** to automate the processing of School ERP fee data and provide interactive dashboards for school administrators.

---

# 🚀 Project Overview

Most school ERP systems provide fee reports in Excel format, making manual analysis time-consuming and prone to errors.

This project automates the complete workflow by reading ERP Excel exports, cleaning and validating the data using Python, storing the processed data in MySQL, and visualizing insights in Power BI.

---

# 🏗️ Project Architecture

```text
School ERP Portal
        │
        ▼
Primary Fees.xlsx
Secondary Fees.xlsx
        │
        ▼
Python ETL Pipeline
(Pandas + Validation)
        │
        ▼
MySQL Database
        │
        ▼
Power BI Dashboard
        │
        ▼
Management Insights
```

---

# 🛠️ Tech Stack

* Python
* Pandas
* MySQL
* SQL
* Power BI
* Excel

---

# 📂 Project Workflow

### Step 1 – ERP Data Export

Fee data is exported from the School ERP system into two Excel files:

* Primary Fees
* Secondary Fees

---

### Step 2 – Python ETL

The Python pipeline automatically:

* Reads ERP Excel exports
* Cleans inconsistent data
* Standardizes column names
* Generates Student IDs
* Extracts Grade & Section
* Calculates Payment Status
* Validates Outstanding Balance
* Creates a cleaned master dataset

---

### Step 3 – MySQL

The cleaned dataset is automatically loaded into the **fees_data** table inside MySQL.

This enables SQL-based analysis and serves as the data source for Power BI.

---

### Step 4 – Power BI Dashboard

The dashboard provides management-level insights through four interactive pages:

## 1️⃣ Principal Overview

* Total Students
* Total Fee Collection
* Total Outstanding
* Outstanding by Grade
* Payment Status Distribution
* Top Defaulters

---

## 2️⃣ Fee Analysis

* Fee Collection Analysis
* Grade-wise Performance
* School-wise Collection
* Outstanding Analysis

---

## 3️⃣ Defaulter Analysis

* Pending Students
* Outstanding Amount
* Defaulter List
* Grade-wise Defaulters

---

## 4️⃣ Student Details

* Student-wise Fee Information
* Payment Status
* Outstanding Balance
* Contact Details
* Interactive Search & Filters

---

# 🔄 Automated ETL Workflow

```text
ERP Excel Export
        ↓
Python ETL
        ↓
Data Cleaning
        ↓
Validation
        ↓
MySQL Update
        ↓
Power BI Refresh
```

The ETL pipeline can be scheduled to run automatically, reducing manual effort and ensuring dashboards stay updated with the latest ERP exports.

---

# ✨ Features

* End-to-End Data Analytics Pipeline
* Automated Python ETL
* Data Cleaning & Validation
* MySQL Database Integration
* SQL Analytics
* Interactive Power BI Dashboard
* KPI Reporting
* Outstanding Fee Analysis
* Defaulter Identification
* Grade-wise Performance Analysis
* School-wise Filtering
* Dynamic Slicers

---

# 📈 Sample Insights

* Total Students
* Total Fee Collected
* Outstanding Balance
* Collection Performance
* Defaulter Identification
* Grade-wise Fee Analysis
* Payment Status Distribution

---

# 📁 Repository Structure

```text
School-ERP-Fee-Performance-Analytics/
│
├── excel_exports/
├── powerbi/
├── python_etl/
├── sql/
├── screenshots/
├── README.md
└── requirements.txt
```

---

# 🔮 Future Enhancements

* Direct ERP API Integration
* Scheduled ETL Execution
* Email Report Automation
* Power BI Service Deployment
* Real-Time Dashboard Refresh

---

# 👨‍💻 Author

**Amroy Pereira**

Data Analyst | Power BI Developer | Python | SQL | Excel

If you found this project useful, feel free to ⭐ the repository.
