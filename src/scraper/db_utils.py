import sqlite3
import os

def get_db_path(data_dir='src/scraper/data', db_name='listings.db'):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, db_name)

def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor

def create_table(cursor):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_type TEXT,
                title TEXT,
                price TEXT,
                sale_rent TEXT,
                bedrooms TEXT,
                bathrooms TEXT,
                parking_space TEXT,
                land_size TEXT,
                floor_size TEXT,
                banner TEXT,           
                link TEXT UNIQUE
            );
        ''')
    except sqlite3.Error as e:
        print(f"An error occurred while creating the table: {e}")
    

def insert_listing(cursor, data):
    cursor.execute('''
        INSERT INTO listings (listing_type, title, price, sale_rent, bedrooms, bathrooms, parking_space, land_size, floor_size, banner, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

def listing_exists(cursor, title, price, bedrooms, bathrooms):
    cursor.execute("SELECT 1 FROM listings WHERE title = ? AND price = ? AND bedrooms = ? AND bathrooms = ?", 
                   (title , price, bedrooms, bathrooms))
    return cursor.fetchone() is not None