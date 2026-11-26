
import requests
import pandas as pd
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import logging

logging.basicConfig(
    filename="scraper_errors.log",
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

products = []

total_pages = 0


def scrape_page(url):

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )
        global total_pages
        total_pages += 1

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        items = soup.select("article.product_pod")

        for item in items:

            name = item.select_one("h3 a")
            price = item.select_one(".price_color")
            availability = item.select_one(
                ".availability"
            )

            product_url = urljoin(
                url,
                name.get("href")
            )

            product = {
                "Product Name": name.get("title"),
                "Price": price.get_text(strip=True),
                "Availability": availability.get_text(
                    strip=True
                ),
                "Product URL": product_url
            }

            products.append(product)

        print(f"Scraped {len(items)} products")

        next_page = soup.select_one(
            "li.next a"
        )

        if next_page:
            next_url = urljoin(
                url,
                next_page.get("href")
            )
            return next_url

        return None

    except requests.RequestException as error:
        logging.error(f"Request error: {error}")
        return None


def main():
    start_time = time.time()
    current_url = START_URL
   

    while current_url:

        current_url = scrape_page(current_url)

        time.sleep(1)

    if products:

        df = pd.DataFrame(products)
        df.drop_duplicates(
            subset=["Product URL"],
            keep="first",
            inplace=True
        )

        print(f"Unique products: {len(df)}")

        df.to_excel(
            "products.xlsx",
            index=False
        )

        print(
            f"Total products scraped: {len(df)}"
        )

        print("Excel file created successfully!")

    else:
        print("No products found")

    end_time = time.time()

    execution_time = round(end_time - start_time, 2)

    print("\n========== SCRAPING SUMMARY ==========")
    print(f"Total Pages Scraped: {total_pages}")
    print(f"Total Products Collected: {len(products)}")
    print(f"Unique Products: {len(df)}")
    print(f"Execution Time: {execution_time} seconds")
    print("Excel Export: Successful")
    print("=====================================")    

       


if __name__ == "__main__":
    main()
