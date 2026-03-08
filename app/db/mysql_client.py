import mysql.connector

def execute_query(sql):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="StrongPassword123",
        database="network_ai"
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)

    result = cursor.fetchall()

    conn.close()

    return result