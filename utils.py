import datetime
import requests

from bs4 import BeautifulSoup

from main import URL


def check_market():
    response = requests.get(URL, verify=False).content
    post = BeautifulSoup(response, "html.parser")
    element = post.select_one("#date_pxs")
    page_date = element["value"]
    expected_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    if page_date == expected_date.strftime("%d.%m.%Y"):
        print("True")
    else:
        print("False")


print(check_market())
