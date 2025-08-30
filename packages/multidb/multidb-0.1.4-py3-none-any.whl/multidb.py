import sqlite3
import psycopg2
import pymysql

def connect(db_type, **kw):
    if db_type == "sqlite":
        conn = sqlite3.connect(kw.get("database", ":memory:"))
        print(f"✅ SQLite connection established to database: {kw.get('database', ':memory:')}")
        return conn

    if db_type == "postgres":
        if "url" in kw:
            conn = psycopg2.connect(kw["url"])
            print("✅ PostgreSQL connection established using URL")
            return conn
        conn = psycopg2.connect(
            host=kw.get("host", "localhost"),
            user=kw["user"],
            password=kw["password"],
            dbname=kw["database"],
            port=kw.get("port", 5432)
        )
        print(f"✅ PostgreSQL connection established to database: {kw['database']} on host: {kw.get('host', 'localhost')}")
        return conn

    if db_type == "mysql":
        conn = pymysql.connect(
            host=kw.get("host", "localhost"),
            user=kw["user"],
            password=kw["password"],
            database=kw["database"],
            port=kw.get("port", 3306)
        )
        print(f"✅ MySQL connection established to database: {kw['database']} on host: {kw.get('host', 'localhost')}")
        return conn

