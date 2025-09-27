import psycopg2
import pandas as pd
from psycopg2 import Error
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
# Database connection settings
# -----------------------------
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")

def parse_timestamp(val):
    """Convert timestamp field safely to datetime or None."""
    if pd.isna(val):
        return None
    try:
        # Some may be float like 1.234e+09, treat as Unix timestamp
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val)
        # Otherwise, try parsing string
        return pd.to_datetime(val, errors="coerce")
    except Exception:
        return None

try:
    print("📂 Loading CSV file...")
    df = pd.read_csv("pakistan.csv")
    print(f"✅ Loaded {len(df)} rows from CSV.")

    print("🔗 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=5432
    )
    cur = conn.cursor()
    print("✅ Connection established.")

    # -----------------------------
    # Create table
    # -----------------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS health_facilities (
        id SERIAL PRIMARY KEY,
        x DOUBLE PRECISION,
        y DOUBLE PRECISION,
        osm_id BIGINT,
        osm_type VARCHAR(50),
        completeness INT,
        is_in_health_zone VARCHAR(50),
        amenity VARCHAR(100),
        speciality VARCHAR(255),
        addr_full TEXT,
        operator VARCHAR(255),
        water_source VARCHAR(255),
        changeset_id BIGINT,
        insurance VARCHAR(255),
        staff_doctors VARCHAR(50),
        contact_number VARCHAR(100),
        uuid VARCHAR(100),
        electricity VARCHAR(50),
        opening_hours VARCHAR(255),
        operational_status VARCHAR(50),
        source VARCHAR(255),
        is_in_health_area VARCHAR(50),
        health_amenity_type VARCHAR(255),
        changeset_version INT,
        emergency VARCHAR(50),
        changeset_timestamp TIMESTAMP,
        name VARCHAR(255),
        staff_nurses VARCHAR(50),
        changeset_user VARCHAR(255),
        wheelchair VARCHAR(50),
        beds VARCHAR(50),
        url TEXT,
        dispensing VARCHAR(50),
        healthcare VARCHAR(100),
        operator_type VARCHAR(100)
    );
    """
    cur.execute(create_table_query)
    conn.commit()
    print("✅ Table is ready.")

    # -----------------------------
    # Insert data
    # -----------------------------
    insert_query = """
    INSERT INTO health_facilities (
        x, y, osm_id, osm_type, completeness, is_in_health_zone, amenity, speciality, addr_full, operator, 
        water_source, changeset_id, insurance, staff_doctors, contact_number, uuid, electricity, opening_hours, 
        operational_status, source, is_in_health_area, health_amenity_type, changeset_version, emergency, 
        changeset_timestamp, name, staff_nurses, changeset_user, wheelchair, beds, url, dispensing, healthcare, operator_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    print("⬆️ Inserting rows...")
    for idx, row in df.iterrows():
        try:
            row_list = list(row)

            # Fix timestamp (assuming column index of changeset_timestamp is 24)
            row_list[24] = parse_timestamp(row_list[24])

            cur.execute(insert_query, tuple(row_list))
            if idx % 100 == 0:
                print(f"   Inserted {idx} rows...")
        except Exception as e:
            print(f"⚠️ Skipping row {idx} due to error: {e}")
            conn.rollback()  # reset transaction so future rows continue

    conn.commit()
    print("✅ All rows inserted successfully.")

except (Exception, Error) as e:
    print("❌ Error:", e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    print("🔒 Connection closed.")
