# dblite.py

import mysql.connector
import sqlite3
from pymongo import MongoClient


def mysql(user, password, host, port):
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )
    print("✅ MySQL connection established.")
    cur = conn.cursor()
    return conn, cur


def sqlite(db_path):
    conn = sqlite3.connect(db_path)
    print("✅ SQLite connection established.")
    cur = conn.cursor()
    return conn, cur


def connect_filess_mongo(mongo_url,mongo_db):
    client = MongoClient(mongo_url)
    db = client[mongo_db]
    print("✅ MongoDB (filess.io) connection established.")
    return client, db


