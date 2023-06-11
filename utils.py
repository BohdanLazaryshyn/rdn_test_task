import csv
import datetime
import sqlite3
from dataclasses import astuple, fields

from model import PricePerHour


PRICE_FIELDS = [field.name for field in fields(PricePerHour)]


def save_to_csv(data: list, date: str) -> None:
    date_now = str(datetime.datetime.now().date())
    date_scraped = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y.%m.%d")
    filename = f"Дата ств-{date_now} за-{date_scraped}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PRICE_FIELDS)
        writer.writerows([astuple(item) for item in data])


def save_to_database(data: list):
    connection = sqlite3.connect("market_data.db")
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
