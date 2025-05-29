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

# Ensure the data directory and get db path
db_path = get_db_path()

# Connect to DB and create table
conn, cursor = connect_db(db_path)
create_table(cursor)

# Set up Chrome options
# Install the ChromeDriver using webdriver_manager
chrome_options = Options()  
chrome_options.headless = True  # Run in headless mode (no GUI)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

while True:
    #Input for the URL
    url = input("Enter a URL from PrivateProperty of the page to scrape: ")
    #Check if the URL is valid
    if url.startswith("https://www.privateproperty.co.za/"):
        break
    else:
        print("Invalid URL. Please enter a valid Private Property URL.")


#Create a new table for the listings
create_table(cursor)

try:
    # Open the URL
    driver.get(url)
    # Example URL: https://www.privateproperty.co.za/to-rent/western-cape/cape-town/55
    # Wait for the page to load
    wait = WebDriverWait(driver, 15)

    # Wait for the element with c be present
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-results-layout__search-results")))

    # Save the page source for debugging
    page_source = driver.page_source
    
except Exception as e:
    print(f"An error occurred: {e}")

soup = BeautifulSoup(page_source, 'html.parser')

# Find the listings container
container = soup.find(class_='listing-results-layout__search-results')
#Count the number of pages
page_num = 1

sale_rent = ''
#Check if the listings are houses for sale or rent
if 'for-sale' in url:
    sale_rent = 'Sale'
else:
    sale_rent = 'Rent'

while True:

    if container:
        #Find all the listings within the container
      for listing in container.find_all('a', class_='listing-result'):
        #Extract the type of listing
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
        
        #Extract the title of the listing
        title_div = listing.find('span', class_='listing-result__mobile-suburb txt-base-bold')
        # Check if the title_div is found before trying to access its text
        # If not found, set a default value
        title = title_div.get_text(strip=True) if title_div else 'No title found'
        # Extract the price of the listing
        price_div = listing.find('div',class_='listing-result__price txt-heading-2')
        # Check if the price_div is found before trying to access its text
        # If not found, set a default value
        if price_div:
            raw_price = price_div.get_text(strip=True)
            # Remove the currency symbol and spaces
            price = ''.join(filter(str.isdigit, raw_price))
            # Check if the price is a valid number
            if price.isdigit():
                price = int(price)
            else:
                price = 'Invalid price'
        else:
            price = 'No price found'

        #Extract the banner of the listing
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

        #Extract the link to the listing
        link = listing.get('href', '')
        # Check if the link is found before trying to access it     
        # If not found, set a default value
        if link:
            link = 'https://www.privateproperty.co.za' + link
        else:   
            link = 'No link found'



        # Initialize default values for features
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

        # Insert the data into the database only if not already present
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

    #Commit the changes to the database
    conn.commit()

    # Check if there is a next page
    try:
        
        # Find the "Next" element
        next_link = driver.find_element(By.LINK_TEXT, 'Next')
        next_href = next_link.get_attribute('href')
        try:
            # Load the next page
            driver.get(next_href)
            # Wait for the new page to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-results-layout__search-results")))
        except Exception as e:
            print(f"An error occurred while finding the next button: {e}")
            break
        page_num += 1
        print(f"Scraping page {page_num}...")
    except Exception as e:
        print(f"An error occurred while clicking the next button: {e}")
        break

    # Make the new loaded page the current page
    soup = BeautifulSoup(driver.page_source, 'html.parser')    

    # Find the listings container again
    container = soup.find(class_='listing-results-layout__search-results')
#Close the driver
driver.quit()
# Close the database connection
conn.close()

