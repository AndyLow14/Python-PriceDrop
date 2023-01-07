import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Delay to allow website to load
WAIT_DELAY = 2

# Chemist warehouse
INC_CHOC = "https://www.chemistwarehouse.com.au/buy/74342/inc-hardgainer-mass-chocolate-flavour-2kg"
CENOVIS_B_COMPLEX = "https://www.chemistwarehouse.com.au/buy/78520/cenovis-b-complex---vitamin-b---150-tablets"
TEST = "https://www.chemistwarehouse.com.au/buy/75858/healthy-care-sugar-balance-plus-90-tablets"

CW_LINKS = [INC_CHOC, CENOVIS_B_COMPLEX, TEST]

# Woolies
MILO = "https://www.woolworths.com.au/shop/productdetails/192985/nestle-milo-choc-malt"
CHOC_UP_AND_GO_PROTEIN = "https://www.woolworths.com.au/shop/productdetails/768911/sanitarium-up-go-protein-energize-choc"
MAMEE_CURRY_LAKSA = "https://www.woolworths.com.au/shop/productdetails/841673/mamee-chef-curry-laksa-cup"
COLGATE_360_TOOTHBRUSH = "https://www.woolworths.com.au/shop/productdetails/200710/colgate-360-optic-white-toothbrush-medium"
CARMANS_PROTEIN_BAR = "https://www.woolworths.com.au/shop/productdetails/175651/carman-s-double-dark-choc-protein-bar"

WOOLIES_LINKS = [MILO, CHOC_UP_AND_GO_PROTEIN, MAMEE_CURRY_LAKSA, COLGATE_360_TOOTHBRUSH, CARMANS_PROTEIN_BAR]


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
    for x in CW_LINKS:
        driver.get(x)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        product_name = soup.find("div", {"itemprop": "name"}).text.strip()
        current_price = soup.find("span", {"class": "product__price"}).text

        print(product_name)
        print(f"Price: {current_price}")

        try:
            price_off = soup.find("div", {"class": "Savings"}).text.strip()
            print(f"Savings: {price_off}\n")
        except:
            print("No price drop")
            pass


def woolies_scraper(driver):
    print("WOOLIES ITEMS\n-------------")
    for x in WOOLIES_LINKS:
        driver.get(x)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # print(soup.text)
        product_name = soup.find("h1", {"class": "shelfProductTile-title heading3"}).text
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
