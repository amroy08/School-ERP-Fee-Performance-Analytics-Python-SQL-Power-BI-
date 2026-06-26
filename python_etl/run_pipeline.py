import os
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ============================================================
# SCHOOL ERP FEE ANALYTICS - AUTOMATED ETL PIPELINE
# ============================================================
# Flow:
# PrimaryFees.xlsx + SecondaryFees.xlsx
#        ↓
# Python ETL Cleaning
#        ↓
# Final_Cleaned_Fees_Data.xlsx
#        ↓
# MySQL fees_data table
# ============================================================


# ------------------------------------------------------------
# 1. Project Paths
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCEL_EXPORTS_DIR = os.path.join(BASE_DIR, "excel_exports")

PRIMARY_FILE = os.path.join(EXCEL_EXPORTS_DIR, "PrimaryFees.xlsx")
SECONDARY_FILE = os.path.join(EXCEL_EXPORTS_DIR, "SecondaryFees.xlsx")

OUTPUT_FILE = os.path.join(EXCEL_EXPORTS_DIR, "Final_Cleaned_Fees_Data.xlsx")

LOG_FILE = os.path.join(BASE_DIR, "python_etl", "etl_log.txt")


# ------------------------------------------------------------
# 2. MySQL Configuration
# ------------------------------------------------------------

MYSQL_USER = "root"
MYSQL_PASSWORD = "1234"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "school_erp_analytics"
MYSQL_TABLE = "fees_data"


# ------------------------------------------------------------
# 3. Logging Function
# ------------------------------------------------------------

def write_log(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{current_time}] {message}"

    print(log_message)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_message + "\n")


# ------------------------------------------------------------
# 4. Clean Single ERP Excel File
# ------------------------------------------------------------

def clean_fee_file(file_path, school_type, id_prefix):
    write_log(f"Reading file: {file_path}")

    # ERP export has first row as title, so actual headers start from row 2
    df = pd.read_excel(file_path, header=1)

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Rename ERP columns to analytics-ready names
    df.rename(
        columns={
            "SN": "sr_no",
            "Name": "student_name",
            "Class": "class",
            "Contact": "contact",
            "Fees": "fees",
            "Old Balance": "old_balance",
            "Total": "total",
            "Received": "received",
            "Outstsnding": "outstanding",
            "Outstanding": "outstanding",
            "Add": "erp_status",
            "Action": "action",
            "Last paid": "last_paid_month",
            "Last Paid": "last_paid_month",
        },
        inplace=True,
    )

    required_cols = [
        "sr_no",
        "student_name",
        "class",
        "contact",
        "fees",
        "old_balance",
        "total",
        "received",
        "outstanding",
        "erp_status",
        "last_paid_month",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing columns in {file_path}: {missing_cols}")

    # Keep only required columns
    df = df[required_cols]

    # Remove empty rows
    df = df.dropna(how="all")

    # Remove rows without student name
    df = df[df["student_name"].notna()]

    # Clean text columns
    df["student_name"] = df["student_name"].astype(str).str.strip()
    df["class"] = df["class"].astype(str).str.strip()
    df["contact"] = df["contact"].astype(str).str.replace(".0", "", regex=False).str.strip()
    df["erp_status"] = df["erp_status"].astype(str).str.strip()
    df["last_paid_month"] = df["last_paid_month"].astype(str).str.strip()

    # Convert numeric columns
    numeric_cols = ["fees", "old_balance", "total", "received", "outstanding"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Extract grade and section from class
    df["grade"] = df["class"].str.extract(r"(\d+)")
    df["section"] = df["class"].str.extract(r"\d+\s*([A-Za-z]+)")

    df["grade"] = pd.to_numeric(df["grade"], errors="coerce")

    # Add school type
    df["school_type"] = school_type

    # Generate student ID
    df["student_id"] = [f"{id_prefix}_{i + 1:03d}" for i in range(len(df))]

    # Create payment status
    def get_payment_status(row):
        if row["outstanding"] <= 0:
            return "Paid"
        elif row["received"] <= 0:
            return "Pending"
        else:
            return "Partial"

    df["payment_status"] = df.apply(get_payment_status, axis=1)

    return df


# ------------------------------------------------------------
# 5. Validate Final Dataset
# ------------------------------------------------------------

def validate_data(final_df):
    write_log("Starting validation checks...")

    total_rows = final_df.shape[0]
    duplicate_students = final_df["student_id"].duplicated().sum()
    missing_students = final_df["student_name"].isna().sum()

    final_df["calculated_outstanding"] = final_df["total"] - final_df["received"]

    mismatch_df = final_df[
        final_df["calculated_outstanding"] != final_df["outstanding"]
    ]

    mismatch_count = mismatch_df.shape[0]

    final_df.drop(columns=["calculated_outstanding"], inplace=True)

    write_log(f"Total rows: {total_rows}")
    write_log(f"Duplicate student IDs: {duplicate_students}")
    write_log(f"Missing student names: {missing_students}")
    write_log(f"Outstanding calculation mismatches: {mismatch_count}")

    if duplicate_students > 0:
        raise ValueError("Duplicate student IDs found.")

    if missing_students > 0:
        raise ValueError("Missing student names found.")

    write_log("Validation checks completed successfully.")


# ------------------------------------------------------------
# 6. Upload Data to MySQL
# ------------------------------------------------------------

def upload_to_mysql(final_df):
    write_log("Connecting to MySQL...")

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        database=MYSQL_DATABASE,
    )

    engine = create_engine(connection_url)

    final_df.to_sql(
        name=MYSQL_TABLE,
        con=engine,
        if_exists="replace",
        index=False,
    )

    write_log(f"MySQL table updated successfully: {MYSQL_TABLE}")


# ------------------------------------------------------------
# 7. Main Pipeline
# ------------------------------------------------------------

def run_pipeline():
    write_log("==========================================")
    write_log("School ERP Fee ETL pipeline started.")

    # Check if input files exist
    if not os.path.exists(PRIMARY_FILE):
        raise FileNotFoundError(f"Primary file not found: {PRIMARY_FILE}")

    if not os.path.exists(SECONDARY_FILE):
        raise FileNotFoundError(f"Secondary file not found: {SECONDARY_FILE}")

    write_log("Input Excel files found.")

    # Clean both files
    primary_df = clean_fee_file(
        file_path=PRIMARY_FILE,
        school_type="Primary",
        id_prefix="PRI",
    )

    secondary_df = clean_fee_file(
        file_path=SECONDARY_FILE,
        school_type="Secondary",
        id_prefix="SEC",
    )

    write_log(f"Primary rows cleaned: {primary_df.shape[0]}")
    write_log(f"Secondary rows cleaned: {secondary_df.shape[0]}")

    # Combine data
    final_df = pd.concat([primary_df, secondary_df], ignore_index=True)

    # Reorder final columns
    final_df = final_df[
        [
            "student_id",
            "sr_no",
            "student_name",
            "school_type",
            "class",
            "grade",
            "section",
            "contact",
            "fees",
            "old_balance",
            "total",
            "received",
            "outstanding",
            "erp_status",
            "payment_status",
            "last_paid_month",
        ]
    ]

    # Validate final dataset
    validate_data(final_df)

    # Save cleaned Excel
    final_df.to_excel(OUTPUT_FILE, index=False)

    write_log(f"Cleaned Excel saved successfully: {OUTPUT_FILE}")

    # Upload to MySQL
    upload_to_mysql(final_df)

    write_log("School ERP Fee ETL pipeline completed successfully.")
    write_log("==========================================")


# ------------------------------------------------------------
# 8. Run Script
# ------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as error:
        write_log(f"ERROR: {str(error)}")
        raise