import mysql.connector

try:
    # Connect to MySQL server
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL@Kampala#2026!"  # Replace with your MySQL password
    )

    cursor = db.cursor()

    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS sensor_db")

    # Select database
    cursor.execute("USE sensor_db")

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        od_value FLOAT,
        pwm_value INT,
        raw_value VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    db.commit()

    print("Database and table created successfully.")

except mysql.connector.Error as err:
    print("MySQL Error:", err)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals() and db.is_connected():
        db.close()