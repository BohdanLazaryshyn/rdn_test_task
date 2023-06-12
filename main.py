import datetime
import time

import requests
import schedule as schedule
from selenium.common import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from models import PricePerHour, URL


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
    table = soup.find("table", class_="site-table")

    data = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 8:
            data.append(get_hour_row(row, date))
    driver.quit()
    return data


def scrap_skript(n: int):       # n - time in seconds to repeat the function call if the table is empty
    date_scraped = datetime.datetime.now().date() + datetime.timedelta(days=1)
    date_scraped = date_scraped.strftime("%d.%m.%Y")
    data = []
    while not data:
        data = get_table(date_scraped)
        if not data:
            print(f"An error occurred on the site, try again in {n} seconds")
            time.sleep(n)
    print(data)
    # save_to_csv(data, date_scraped)           # uncomment for the possibility of saving in a file
    # save_to_database(data)                    # uncomment for the possibility of saving in a database
    return True


def check_market(seconds: int = 2):         # seconds - time for "scrap_skript"
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    expected_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    expected_date = expected_date.strftime("%d.%m.%Y")
    if page_date == expected_date:
        scrap_skript(seconds)
        return True


def job():
    while not check_market(2):
        time.sleep(300)             # 300 seconds = 5 minutes (the market is checked every 5 minutes)
        print("Wait for the next check...")
    print("The market is closed, wait for the result...")
    schedule.clear()                # clear the schedule after the market closes


def main():                 # running a script to check the market close every day starting at 12:00
    schedule.every().day.at("12:00").do(job)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()
