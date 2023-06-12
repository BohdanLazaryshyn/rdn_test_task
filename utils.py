import requests
from bs4 import BeautifulSoup
from flask import flash
from selenium.common import WebDriverException

from models import PricePerHour

URL = "https://www.oree.com.ua/index.php/control/results_mo/DAM"


def check_connection():
    try:
        response = requests.get(URL, verify=False)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        flash("Помилка з'єднання, перевірте мережу:", str(e))


def check_connection_for_driver(driver, url: str):
    try:
        driver.get(url)
    except WebDriverException as e:
        raise Exception("Помилка з'єднання:", str(e))


def get_hour_row(row: BeautifulSoup, date: str) -> PricePerHour:  # get the data from the row of the table
    return PricePerHour(
        date_of_parsing=date,
        hour=int(row.select_one("td:nth-child(2)").text),
        price=float(row.select_one("td:nth-child(3)").text),
        sales_volume_MWh=float(row.select_one("td:nth-child(4)").text),
        purchase_volume_MWh=float(row.select_one("td:nth-child(5)").text),
        declared_sales_volume_MWh=float(row.select_one("td:nth-child(6)").text),
        declared_purchase_volume_MWh=float(row.select_one("td:nth-child(7)").text),
    )


def get_date():                       # get the date of the last possible market close
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    return page_date
