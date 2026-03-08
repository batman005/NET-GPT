import mysql.connector


def load_schema():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="StrongPassword123",
        database="network_ai"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'network_ai'
    """)

    rows = cursor.fetchall()

    schema = {}

    for table, column in rows:
        if table not in schema:
            schema[table] = []

        schema[table].append(column)

    cursor.close()
    conn.close()

    return schema


