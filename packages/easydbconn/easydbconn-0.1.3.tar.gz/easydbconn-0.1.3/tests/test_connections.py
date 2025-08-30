from easydbconn import sqlite
from easydbconn import mysql
from easydbconn import postgres

# Connect to an in-memory database or a file
conn_sqlite, cur_sqlite = sqlite(":memory:") 

if conn_sqlite:
    cur_sqlite.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    cur_sqlite.execute("INSERT INTO users VALUES (?, ?)", (1, "Alice"))
    conn_sqlite.commit()
    cur_sqlite.execute("SELECT * FROM users")
    print("SQLite users:", cur_sqlite.fetchall())
    conn_sqlite.close()


conn_mysql, cur_mysql = mysql(
    user="root", 
    password="Rohidas@2003",
    host="127.0.0.1", 
    port=3306,
)

if conn_mysql:
    cur_mysql.execute("SELECT * FROM actor LIMIT 5")
    print("MySQL actors:", cur_mysql.fetchall())
    conn_mysql.close()



# Your URI from filess.io will look something like this
POSTGRES_URI = "postgresql://ForLibeary_biggestshe:823f56ed1455a4f8ec319c12870ed24c9115b8ac@ino4p0.h.filess.io:5432/ForLibeary_biggestshe"

conn_pg, cur_pg = postgres(POSTGRES_URI)

if conn_pg:
    cur_pg.execute("SELECT version()")
    print("PostgreSQL Version:", cur_pg.fetchone())
    conn_pg.close()