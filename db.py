import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        autocommit=True
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content_text TEXT,
                image_path VARCHAR(255),
                analysis TEXT,
                timestamp DATETIME
            )"""
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS summaries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                day DATE UNIQUE,
                summary_text TEXT
            )"""
    )
    cursor.close()
    conn.close()


def add_entry(text, image_path, analysis):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (content_text, image_path, analysis, timestamp) VALUES (%s, %s, %s, %s)",
        (text, image_path, analysis, datetime.now())
    )
    cursor.close()
    conn.close()


def get_entries_between(start_dt, end_dt):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM entries WHERE timestamp >= %s AND timestamp < %s ORDER BY timestamp",
        (start_dt, end_dt)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def save_summary(day: date, summary_text: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO summaries (day, summary_text) VALUES (%s, %s)",
        (day, summary_text)
    )
    cursor.close()
    conn.close()


def get_summaries(limit=365):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM summaries ORDER BY day DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


