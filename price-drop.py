import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

f = open("watchlist.json", "r")
watchlist = json.load(f)
f.close()

# Delay to allow website to load
WAIT_DELAY = 2

CW_BASE = "https://www.chemistwarehouse.com.au/buy/"
WOOLIES_BASE = "https://www.woolworths.com.au/shop/productdetails/"

def main():
    print("Fetching prices...")
    # Scraping the website
    options = Options()
    # Hides the firefox window when selenium is executing
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
   
    print_date()
    cw_scraper(driver)
    print_divider()
    woolies_scraper(driver)

    driver.close()
    input("Press enter to close...")


def print_date():
    date_scanned = datetime.now().strftime("%d %b | %I:%M %p")
    print(f"Date scanned: {date_scanned}")
    print_divider()


# Finds the elements of interest in the html page (chemist_warehouse)
def cw_scraper(driver):
    print("CHEMIST WAREHOUSE ITEMS\n-----------------------")
    for cwid in watchlist["Chemist_Warehouse"].values():
        full_link = CW_BASE + cwid
        driver.get(full_link)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        product_name = soup.find("div", {"itemprop": "name"}).text.strip()
        current_price = soup.find("span", {"class": "product__price"}).text

        print(product_name)
        print(f"Price: {current_price}")

        try:
            price_off = soup.find("div", {"class": "Savings"}).text.strip()
            curr_price_f = float(current_price.replace("$", ""))
            price_off_f = float(re.findall(r'\$([\d.]+)', price_off)[0])

            percentage_drop = round((1 - (curr_price_f / (price_off_f + curr_price_f))) * 100)
            print(f"Savings: {price_off} (-{percentage_drop}%)\n")
        except:
            print("No price drop \n")
            pass


def woolies_scraper(driver):
    print("WOOLIES ITEMS\n-------------")
    for wlid in watchlist["Woolworths"].values():
        full_link = WOOLIES_BASE + wlid
        driver.get(full_link)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # print(soup.text)
        product_name = soup.find("h1", {"class": "shelfProductTile-title"}).text
        current_price_dollars = WebDriverWait(driver, WAIT_DELAY).until(EC.presence_of_element_located((By.CLASS_NAME, "price-dollars"))).text
        current_price_cents = WebDriverWait(driver, WAIT_DELAY).until(EC.presence_of_element_located((By.CLASS_NAME, "price-cents"))).text
        curr_price = f"{current_price_dollars}.{current_price_cents}"
        curr_price_f = float(curr_price)
        
        print(product_name)
        print(f"Price: ${curr_price}")

        try:
            price_was = WebDriverWait(driver, WAIT_DELAY).until(EC.presence_of_element_located((By.CLASS_NAME, "price-was")))
            price_was = price_was.text
            # Slice the string to remove the "was and $ sign"
            was_price_f = float(re.findall(r'\d+\.\d+', price_was)[0])
            percentage_drop = round((1-(curr_price_f/was_price_f))*100)
            print(price_was)
            print(f"Price drop: -{percentage_drop}%\n")
        except:
            # Price was element is not found, no drop in price!!
            print("No price drop\n")
        
def print_divider():
    print("-----------------------------------------------------")   
    
if __name__ == "__main__":
    main()
