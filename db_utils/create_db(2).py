import psycopg2

# Database connection URL

def create_tables():
    conn = None
    try:
        print("🔗 Connecting to PostgreSQL...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        # Create chat table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                from_user TEXT NOT NULL,
                topic TEXT,
                session_id VARCHAR(100) NOT NULL
            );
        """)

        # Create summary table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS summary (
                id SERIAL PRIMARY KEY,
                summary_text TEXT NOT NULL,
                session_id VARCHAR(100) NOT NULL
            );
        """)

        # Create appointment table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                department TEXT NOT NULL,
                time TIMESTAMP NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(150),
                phone VARCHAR(20)
            );
        """)

        # Create wantAppointments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wantAppointments (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                wants_appointment BOOLEAN NOT NULL
            );
        """)

        conn.commit()
        cur.close()
        print("✅ All tables created successfully.")

    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_tables()
