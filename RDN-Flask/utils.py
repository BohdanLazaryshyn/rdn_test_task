import csv
import datetime
import sqlite3
from dataclasses import astuple, fields

import requests
from bs4 import BeautifulSoup

from models import PricePerHour, URL

PRICE_FIELDS = [field.name for field in fields(PricePerHour)]     # get the names of the fields of the PricePerHour class


def get_date():                       # get the date of the last possible market close
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    return page_date


def save_to_csv(data: list, date: str) -> None:      # save data to csv file (optional)
    date_now = str(datetime.datetime.now().date())
    date_scraped = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y.%m.%d")
    filename = f"Дата ств-{date_now} за-{date_scraped}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PRICE_FIELDS)
        writer.writerows([astuple(item) for item in data])


def save_to_database(data: list):            # save data to database (optional)
    connection = sqlite3.connect("../market_data.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_of_parsing TEXT NOT NULL,
            hour INTEGER NOT NULL,
            price REAL NOT NULL,
            sales_volume_MWh REAL NOT NULL,
            purchase_volume_MWh REAL NOT NULL,
            declared_sales_volume_MWh REAL NOT NULL,
            declared_purchase_volume_MWh REAL NOT NULL
        )
        """
    )
    cursor.executemany(
        """
        INSERT INTO market_data (
            date_of_parsing,
            hour,
            price,
            sales_volume_MWh,
            purchase_volume_MWh,
            declared_sales_volume_MWh,
            declared_purchase_volume_MWh
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [(item.date_of_parsing, item.hour, item.price, item.sales_volume_MWh,
          item.purchase_volume_MWh, item.declared_sales_volume_MWh, item.declared_purchase_volume_MWh) for item in data]
    )
    connection.commit()
    connection.close()
