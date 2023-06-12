import datetime
import time

from bs4 import BeautifulSoup
from flask import request, jsonify, render_template, flash
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.common.by import By

from config import app, db
from utils import (
    get_date,
    get_hour_row,
    check_connection_for_driver,
    check_connection,
    URL)

from models import PricePerHour

last_date = get_date()  # last date for which data is available


def check_date(date: str) -> bool:
    try:
        datetime.datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        flash("Невірний формат дати. Повинно бути: дд.мм.рррр, наприклад 01.01.2021")
        return True
    first_date = datetime.datetime.strptime("01.07.2019", "%d.%m.%Y")
    if datetime.datetime.strptime(date, "%d.%m.%Y") < first_date:
        flash("Дата повинна бути після 01.07.2019")
        return True
    if datetime.datetime.strptime(date, "%d.%m.%Y") > datetime.datetime.strptime(last_date, "%d.%m.%Y"):
        flash(f"Остання доступна дата: {last_date}")
        return True


def get_table(date: str) -> list:
    driver = Chrome()
    check_connection_for_driver(driver, URL)
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, "tab-trade-res")
    if element.text == "Погодинні результати на РДН":
        element.click()
    time.sleep(1)
    if datetime.datetime.strptime(date, "%d.%m.%Y") < datetime.datetime.now():   # if date is in the past
        calendar = driver.find_element(By.ID, "date_pxs")
        calendar.clear()
        calendar.send_keys(date)
        time.sleep(0.5)
        calendar.send_keys(Keys.ENTER)
        time.sleep(3)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table", class_="site-table")

    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 8:
                hour_row = get_hour_row(row, date)
                db.session.add(hour_row)
                db.session.commit()
                data.append(hour_row.to_dict())
    driver.close()
    return data


@app.route("/", methods=["GET"])
def date_form():

    return render_template("market_page.html")


@app.route("/data", methods=["GET"])
def get_data_from_market():
    if not check_connection():
        return render_template("market_page.html")
    date = request.args.get("date")
    if not date:
        date = last_date
    else:
        if check_date(date):
            return render_template("market_page.html")
    if PricePerHour.query.filter_by(date_of_parsing=date).all() != []:
        flash("Дані за цю дату вже збережено в базу даних")
        return render_template("market_page.html")
    data = []
    while not data:
        data = get_table(date)
    return jsonify({"data": data}), 200


@app.route("/db", methods=["GET"])
def get_data_from_db():
    date = request.args.get("date")
    if not date:
        date = last_date
    else:
        if check_date(date):
            return render_template("market_page.html")
    hours = PricePerHour.query.filter_by(date_of_parsing=date).all()
    data = []
    for hour in hours:
        data.append({
            "id": hour.id,
            "date_of_parsing": hour.date_of_parsing,
            "hour": hour.hour,
            "price": hour.price,
            "sales_volume_MWh": hour.sales_volume_MWh,
            "purchase_volume_MWh": hour.purchase_volume_MWh,
            "declared_sales_volume_MWh": hour.declared_sales_volume_MWh,
            "declared_purchase_volume_MWh": hour.declared_purchase_volume_MWh,
        })
    return jsonify({"data": data}), 200


if __name__ == '__main__':
    app.run()
