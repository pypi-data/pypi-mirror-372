import mysql.connector as mysql_connector
import sqlite3
import psycopg2 

def mysql(user, password, host, port, database=None):
    """Establishes a connection to a MySQL database."""
    try:
        conn = mysql_connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("✅ MySQL connection established.")
        cur = conn.cursor()
        return conn, cur
    except mysql_connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None, None

def sqlite(db_path):
    """Establishes a connection to a SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        print("✅ SQLite connection established.")
        cur = conn.cursor()
        return conn, cur
    except sqlite3.Error as err:
        print(f"Error connecting to SQLite: {err}")
        return None, None

def postgres(uri):
    """
    Establishes a connection to a PostgreSQL database using a connection URI.
    Example URI: postgresql://user:password@host:port/database
    """
    try:
        conn = psycopg2.connect(uri)
        print("✅ PostgreSQL connection established.")
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as err:
        print(f"Error connecting to PostgreSQL: {err}")
        return None, None