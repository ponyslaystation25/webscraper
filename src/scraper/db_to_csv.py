import sqlite3
import pandas as pd

def db_to_csv(db_path, csv_path):

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Read the data from the database into a DataFrame
    df = pd.read_sql_query("SELECT * FROM listings", conn)
    
    # Write the DataFrame to a CSV file
    df.to_csv(csv_path, index=False)
    
    # Close the database connection
    conn.close()

def csv_to_db(csv_path, db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Prepare the insert statement
    insert_sql = '''
        INSERT INTO listings (listing_type, title, price, sale_rent, bedrooms, bathrooms, parking_space, land_size, floor_size, banner, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    # Iterate through DataFrame rows
    for _, row in df.iterrows():
        # Check if the listing already exists
        cursor.execute(
            "SELECT 1 FROM listings WHERE title=? AND price=? AND bedrooms=? AND bathrooms=?",
            (row['title'], row['price'], row['bedrooms'], row['bathrooms'])
        )
        if cursor.fetchone() is None:
            cursor.execute(insert_sql, (
                row['listing_type'],
                row['title'],
                row['price'],
                row['sale_rent'],
                row['bedrooms'],
                row['bathrooms'],
                row['parking_space'],
                row['land_size'],
                row['floor_size'],
                row['banner'],
                row['link']
            ))

    conn.commit()
    conn.close()