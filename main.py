import csv
import datetime
import time

from dataclasses import dataclass, fields, astuple

from selenium.common import WebDriverException
from selenium.webdriver import Chrome, Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

URL = "https://www.oree.com.ua/index.php/control/results_mo/DAM"


@dataclass
class PricePerHour:
    date_of_parsing: str
    hour: int
    price: float
    sales_volume_MWh: float
    purchase_volume_MWh: float
    declared_sales_volume_MWh: float
    declared_purchase_volume_MWh: float


PRICE_FIELDS = [field.name for field in fields(PricePerHour)]


def get_hour_row(row: BeautifulSoup, date) -> PricePerHour:
    return PricePerHour(
        date_of_parsing=date,
        hour=int(row.select_one("td:nth-child(2)").text),
        price=float(row.select_one("td:nth-child(3)").text),
        sales_volume_MWh=float(row.select_one("td:nth-child(4)").text),
        purchase_volume_MWh=float(row.select_one("td:nth-child(5)").text),
        declared_sales_volume_MWh=float(row.select_one("td:nth-child(6)").text),
        declared_purchase_volume_MWh=float(row.select_one("td:nth-child(7)").text),
    )


def save_to_csv(data: list, date: str = str(datetime.datetime.now().date())) -> None:
    date_now = str(datetime.datetime.now().date())
    filename = f"Дата ств-{date_now} за-{date}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PRICE_FIELDS)
        writer.writerows([astuple(item) for item in data])


def check_connection(driver, url: str):
    try:
        driver.get(url)
    except WebDriverException as e:
        raise ("Помилка з'єднання:", str(e))


def check_date(date: str) -> bool:
    try:
        datetime.datetime.strptime(date, "%d.%m.%Y")
        return True
    except ValueError:
        print("Невірний формат дати. Повинно бути: дд.мм.рррр")


def get_date():
    date = input("Введіть дату у форматі дд.мм.рррр: ")
    while not check_date(date):
        date = input("Введіть дату у форматі дд.мм.рррр: ")
    return date


def get_table(date: str = str(datetime.datetime.now().date())) -> list:
    driver = Chrome()
    check_connection(driver, URL)
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, "tab-trade-res")
    if element.text == "Погодинні результати на РДН":
        element.click()
    time.sleep(1)                                                   # work with datepicker
    calendar = driver.find_element(By.ID, "date_pxs")
    calendar.clear()
    calendar.send_keys(date)
    time.sleep(0.5)
    calendar.send_keys(Keys.ENTER)
    time.sleep(5)                   # work with datepicker end
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table", class_="site-table")    #clasik script

    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 8:
                data.append(get_hour_row(row, date))

    driver.close()
    return data


def get_info(n: int = 2):
    date = get_date()           # n - time in seconds to repeat the function call if the table is empty (default 2)
    data = []
    while not data:
        data = get_table(date)
        if not data:
            print(f"An error occurred on the site, try again in {n} seconds")
            time.sleep(n)
    print(data)
    save_to_csv(data, date)


if __name__ == '__main__':
    get_info()
