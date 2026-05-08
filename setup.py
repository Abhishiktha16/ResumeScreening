import psycopg2

def setup_database():
    try:
        # Connect to the database. Adjust these if your local setup uses different credentials.
        conn = psycopg2.connect(
            host="localhost",
            database="resume_db",
            user="postgres",
            password="123456"
        )
        cur = conn.cursor()

        print("Connected to resume_db successfully!")

        # Create hr_users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hr_users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        print("Created table: hr_users")

        # Create jobs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                company VARCHAR(255),
                job_profile VARCHAR(255),
                salary VARCHAR(100),
                job_description VARCHAR(255),
                posted_by VARCHAR(255),
                posted_at TIMESTAMP
            )
        """)
        print("Created table: jobs")

        # Create resumes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                filename VARCHAR(255),
                job_id INTEGER,
                score FLOAT,
                status VARCHAR(50),
                uploaded_at TIMESTAMP
            )
        """)
        print("Created table: resumes")

        conn.commit()
        cur.close()
        conn.close()
        print("Database setup complete! You are ready to run app.py.")

    except psycopg2.Error as e:
        print("Error connecting to or setting up the database:")
        print(e)
        print("Please make sure PostgreSQL is installed, running, and the credentials match.")

if __name__ == "__main__":
    setup_database()