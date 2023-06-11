import secrets
import datetime
import time
import requests

from flask import Flask, request, jsonify, render_template, flash
from selenium.common import WebDriverException
from selenium.webdriver import Chrome, Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from model import PricePerHour
from utils import save_to_csv, save_to_database

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = secrets.token_hex(16)

URL = "https://www.oree.com.ua/index.php/control/results_mo/DAM"


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


def get_date():
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    expected_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    expected_date = expected_date.strftime("%d.%m.%Y")
    if page_date == expected_date:
        return expected_date
    else:
        return datetime.datetime.now().date().strftime("%d.%m.%Y")


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


def get_table(date: str) -> list:
    driver = Chrome()
    check_connection_for_driver(driver, URL)
    time.sleep(3)
    element = driver.find_element(By.CLASS_NAME, "tab-trade-res")
    if element.text == "Погодинні результати на РДН":
        element.click()
    time.sleep(1)
    if datetime.datetime.strptime(date, "%d.%m.%Y") < datetime.datetime.now():
        calendar = driver.find_element(By.ID, "date_pxs")
        calendar.clear()
        calendar.send_keys(date)
        time.sleep(0.5)
        calendar.send_keys(Keys.ENTER)
        time.sleep(3)                   # work with datepicker end
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table", class_="site-table")

    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 8:
                data.append(get_hour_row(row, date))
    driver.close()
    return data


@app.route("/", methods=["GET"])
def date_form():
    return render_template("market_page.html")


@app.route("/data", methods=["GET"])
def get_data():
    if not check_connection():
        return render_template("market_page.html")
    date = request.args.get("date")
    if not date:
        date = get_date()
        if not date:
            return render_template("market_page.html")
    else:
        if check_date(date):
            return render_template("market_page.html")

    data = []
    while not data:
        data = get_table(date)

    save_to_csv(data, date)
    save_to_database(data)
    return jsonify({"data": data}), 200


if __name__ == '__main__':
    app.run()
