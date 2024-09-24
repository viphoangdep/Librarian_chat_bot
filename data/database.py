import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(
        dbname="library_management",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

def fetch_books_to_dataframe():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM books;"
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    finally:
        cursor.close()
        conn.close()
    
    return df
