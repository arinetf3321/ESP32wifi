import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL@Kampala#2026!"
    )

    print("Connected successfully!")

    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")

    result = cursor.fetchone()
    print("MySQL Version:", result[0])

except Exception as e:
    print("Connection failed:", e)