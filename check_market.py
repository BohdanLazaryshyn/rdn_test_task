import datetime

import requests

from bs4 import BeautifulSoup

from main import URL, scrap_skript


def check_market():
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    expected_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    expected_date = expected_date.strftime("%d.%m.%Y")
    if page_date == expected_date:
        scrap_skript(1)


print(check_market())
