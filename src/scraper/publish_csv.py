from db_to_csv import db_to_csv
import os

def publish_csv():
    data_dir = 'src/scraper/data'
    local_dir = 'C:\\Users\\zanes\\OneDrive\\Desktop\\Application_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_path = os.path.join(data_dir, 'listings.db')
    csv_path = os.path.join(data_dir, 'listings.csv')
    local_csv_path = os.path.join(local_dir, 'listings.csv')

    # Convert database to CSV and save it in the data directory
    db_to_csv(db_path, csv_path)
    # Copy the CSV file to the local directory
    db_to_csv(db_path, local_csv_path)

