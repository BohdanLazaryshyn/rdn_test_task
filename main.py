import datetime
import time

from selenium.common import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from model import PricePerHour
from utils import save_to_csv, save_to_database

URL = "https://www.oree.com.ua/index.php/control/results_mo/DAM"


def get_hour_row(row: BeautifulSoup, date: str) -> PricePerHour:
    return PricePerHour(
        date_of_parsing=date,
        hour=int(row.select_one("td:nth-child(2)").text),
        price=float(row.select_one("td:nth-child(3)").text),
        sales_volume_MWh=float(row.select_one("td:nth-child(4)").text),
        purchase_volume_MWh=float(row.select_one("td:nth-child(5)").text),
        declared_sales_volume_MWh=float(row.select_one("td:nth-child(6)").text),
        declared_purchase_volume_MWh=float(row.select_one("td:nth-child(7)").text),
    )


def check_connection(driver, url: str):
    try:
        driver.get(url)
    except WebDriverException:
        raise Exception("Помилка з'єднання зі сторінкою, перевірте мережу")


def get_table(date: str) -> list:
    service = Service("/usr/local/bin/chromedriver")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    check_connection(driver, URL)
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, "tab-trade-res")
    if element.text == "Погодинні результати на РДН":
        element.click()
    time.sleep(1)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table", class_="site-table")    # classic script

    data = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 8:
            data.append(get_hour_row(row, date))
    driver.close()
    return data


def scrap_skript(n: int = 2):       # n - time in seconds to repeat the function call if the table is empty (default 2)
    date_scraped = datetime.datetime.now().date() + datetime.timedelta(days=1)
    date_scraped = date_scraped.strftime("%d.%m.%Y")
    data = []
    while not data:
        data = get_table(date_scraped)
        if not data:
            print(f"An error occurred on the site, try again in {n} seconds")
            time.sleep(n)
    print(data)
    save_to_csv(data, date_scraped)
    save_to_database(data)


if __name__ == '__main__':
    scrap_skript()
