import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Chemist warehouse
INC_CHOC_URL = "https://www.chemistwarehouse.com.au/buy/74342/inc-hardgainer-mass-chocolate-flavour-2kg"

# Woolies
LINK = "https://www.woolworths.com.au/shop/productdetails/159019/airborne-manuka-honey-upside-down"
LINK2 = "https://www.woolworths.com.au/shop/productdetails/717255/sanitarium-up-go-liquid-breakfast-choc-ice"
LINKS = [LINK, LINK2]


def main():
    print("Fetching prices...")
    # Scraping the website
    options = Options()
    # Hides the firefox window when selenium is executing
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
   
    print_date()
    #cw_scraper(driver)
    woolies_scraper(driver)

    driver.close()
    input("Press enter to close...")


def print_date():
    date_scanned = datetime.now().strftime("%d %b | %I:%M %p")
    print(f"Date: {date_scanned}")


# Finds the elements of interest in the html page (chemist_warehouse)
def cw_scraper(driver):
    driver.get(INC_CHOC_URL)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    product_name = soup.find("div", {"itemprop": "name"}).text.strip()
    current_price = soup.find("span", {"class": "product__price"}).text
    price_off = soup.find("div", {"class": "Savings"}).text.strip()

    print(product_name)
    print(f"Price: {current_price}")
    print(f"Savings: {price_off}")

def woolies_scraper(driver):

    for x in LINKS:
        driver.get(x)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # print(soup.text)
        product_name = soup.find("h1", {"class": "shelfProductTile-title heading3"}).text
        current_price_dollars = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "price-dollars"))).text
        current_price_cents = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "price-cents"))).text
        curr_price = f"{current_price_dollars}.{current_price_cents}"
        curr_price_f = float(curr_price)
        
        print(product_name)
        print(f"Price: ${curr_price}")

        try:
            price_was = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "price-was")))
            price_was = price_was.text
            # Slice the string to remove the "was and $ sign"
            was_price_f = float(re.findall(r'\d+\.\d+', price_was)[0])
            percentage_drop = round((1-(curr_price_f/was_price_f))*100)
            print(price_was)
            print(f"Price drop: -{percentage_drop}%")
        except:
            # Price was element is not found, no drop in price!!
            print("Price unchanged")
        
        
def print_divider():
    print("---------------------------------------------------------------------------------")   
    
if __name__ == "__main__":
    main()
