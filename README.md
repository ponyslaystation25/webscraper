# PrivateProperty Web Scraper

## Main Use Case
This web scraper automates the extraction of property listings from [PrivateProperty.co.za](https://www.privateproperty.co.za/) using Selenium and BeautifulSoup.  
It collects details such as property type, title, price, bedrooms, bathrooms, parking spaces, land size, floor size, banner status, and listing link.

## How It Works
- The application prompts the user for a PrivateProperty search results URL (e.g., `https://www.privateproperty.co.za/for-sale/western-cape/cape-town/55`).
- It scrapes all pages of results, collecting property information.
- Data is stored in a local SQLite database (`listings.db`) and exported to a CSV file (`listings.csv`).
- Duplicate listings are avoided based on title, price, bedrooms, and bathrooms.
- After scraping, the CSV is also copied to a user-specified directory (see `publish_csv.py`).

## Project Structure
- **scraper.py**: Main entry point; handles user interaction, scraping, and database operations.
- **db_utils.py**: Database helper functions (connect, create table, insert, check for duplicates).
- **db_to_csv.py**: Functions to export/import between the database and CSV.
- **publish_csv.py**: Exports the database to CSV and copies it to a specified directory.
- **src/scraper/data/**: Default location for the database and CSV files.
- **README.md**: Project documentation.

## Setup & Usage

1. **Install dependencies**  
   ```
   pip install -r requirements.txt
   ```
   (Make sure you have Chrome installed for Selenium.)

2. **Run the scraper**  
   ```
   python src/scraper/scraper.py
   ```
   - Enter the PrivateProperty URL when prompted.
   - After scraping, the data will be saved to both the database and CSV.

3. **Export CSV to a custom location**  
   - By default, the CSV is also copied to the folder specified by `local_dir` in `publish_csv.py`.
   - **Change `local_dir`** in `publish_csv.py` to your preferred destination.

4. **Build an executable (optional)**  
   - Use PyInstaller to create a standalone `.exe`:
     ```
     pyinstaller --onefile src/scraper/scraper.py
     ```

## Notes
- The scraper only processes listings with type "Apartment" or "House".
- The database prevents duplicate entries using a combination of title, price, bedrooms, and bathrooms.
- You can scrape multiple URLs in one session; the scraper will prompt after each batch.
- If you want to change where the CSV is saved, edit the `local_dir` variable in `publish_csv.py`.

## Requirements
- Python 3.8+
- Google Chrome (for Selenium)
- See `requirements.txt` for Python dependencies.

---