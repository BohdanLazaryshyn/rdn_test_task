from dataclasses import dataclass

URL = "https://www.oree.com.ua/index.php/control/results_mo/DAM"    # URL of the page with the table


@dataclass
class PricePerHour:           # dataclass for storing data from the table
    date_of_parsing: str
    hour: int
    price: float
    sales_volume_MWh: float
    purchase_volume_MWh: float
    declared_sales_volume_MWh: float
    declared_purchase_volume_MWh: float
