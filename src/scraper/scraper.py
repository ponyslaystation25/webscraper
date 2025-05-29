from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
from db_utils import get_db_path, connect_db, create_table, insert_listing, listing_exists
from publish_csv import publish_csv

def setup_driver():
    chrome_options = Options()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def scrape_page(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-results-layout__search-results")))
        return driver.page_source
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_listings(soup, sale_rent, cursor):
    container = soup.find(class_='listing-results-layout__search-results')
    if not container:
        print("No listings container found.")
        return False

    for listing in container.find_all('a', class_='listing-result'):
        # Extract type
        type_div = listing.find('div', class_='listing-result__title txt-base-regular')
        if type_div:
            type_text = type_div.get_text(strip=True)
            if "Apartment" in type_text:
                listing_type = "Apartment"
            elif "House" in type_text:
                listing_type = "House"
            else:
                listing_type = "Other"
        else:
            listing_type = "Unknown"

        # Title
        title_div = listing.find('span', class_='listing-result__mobile-suburb txt-base-bold')
        # Check if the title_div is found before trying to access its text
        # If not found, set a default value
        title = title_div.get_text(strip=True) if title_div else 'No title found'

        # Price
        price_div = listing.find('div', class_='listing-result__price txt-heading-2')
        if price_div:
            raw_price = price_div.get_text(strip=True)
            # Remove the currency symbol and spaces
            price = ''.join(filter(str.isdigit, raw_price))
            price = int(price) if price.isdigit() else 'Invalid price'
        else:
            price = 'No price found'

        # Banner
        banner_div = listing.find('div', class_='listing-banner listing-banner--sold')
        banner_div2 = listing.find('div', class_='listing-banner listing-banner--offer-pending')
        # Check if the banner_div is found before trying to access its text
        # If not found, set a default value
        if banner_div:
            banner = banner_div.get_text(strip=True)
        elif banner_div2:
            banner = banner_div2.get_text(strip=True)
        else:
            banner = 'No banner found'

        # Link
        link = listing.get('href', '')
        link = 'https://www.privateproperty.co.za' + link if link else 'No link found'

        # Features
        features = {
            'Bedrooms': 'No beds found',
            'Bathrooms': 'No baths found',
            'Parking spaces': 'No parking found',
            'Land size': 'No land size found',
            'Floor size': 'No floor size found',
            'Banner': banner,
            'Link': link
        }

        # Extract the listing result features per feature using an index
        for feature in listing.find_all('span', class_='listing-result__feature'):
            feature_title = feature.get('title', '')
            if feature_title in features:
                features[feature_title] = feature.get_text(strip=True)

        # First remove the 'm²' from the land size and floor size
        if features['Land size'] != 'No land size found':
            features['Land size'] = features['Land size'].replace('m²', '').strip()
        if features['Floor size'] != 'No floor size found':
            features['Floor size'] = features['Floor size'].replace('m²', '').strip()

        # Insert into DB if not exists
        try:
            if not listing_exists(cursor, title, price, features['Bedrooms'], features['Bathrooms']):
                insert_listing(cursor, (
                    listing_type,
                    title,
                    price,
                    sale_rent,
                    features['Bedrooms'],
                    features['Bathrooms'],
                    features['Parking spaces'],
                    features['Land size'],
                    features['Floor size'],
                    features['Banner'],
                    features['Link']
                ))
                print(f"Inserted listing: {title} with price: {price}")
            else:
                print("Listing already exists in DB")
        except Exception as e:
            print(f"An error occurred while inserting data into the database: {e}")
    return True

def paginate_and_scrape(driver, url, sale_rent, cursor, conn):
    page_num = 1
    while True:
        page_source = scrape_page(driver, url)
        if not page_source:
            break
        soup = BeautifulSoup(page_source, 'html.parser')
        found = extract_listings(soup, sale_rent, cursor)
        conn.commit()
        if not found:
            break
        # Try to find the next page
        try:
            next_link = driver.find_element(By.LINK_TEXT, 'Next')
            next_href = next_link.get_attribute('href')
            url = next_href
            page_num += 1
            print(f"Scraping page {page_num}...")
        except Exception:
            print("No more pages.")
            break

def main():
    db_path = get_db_path()
    conn, cursor = connect_db(db_path)
    create_table(cursor)
    driver = setup_driver()

    try:
        while True:
            url = input("Enter a URL from PrivateProperty of the page to scrape: ")
            if not url.startswith("https://www.privateproperty.co.za/"):
                print("Invalid URL. Please enter a valid Private Property URL.")
                continue

            sale_rent = 'Sale' if 'for-sale' in url else 'Rent'
            paginate_and_scrape(driver, url, sale_rent, cursor, conn)

            another = input("Do you want to scrape another URL? (y/n): ").strip().lower()
            if another != 'y':
                break
    finally:
        # Publish the data to CSV
        publish_csv()
        print("Scraping completed and data published to CSV.")

        driver.quit()
        conn.close()
    
        

if __name__ == "__main__":
    main()

