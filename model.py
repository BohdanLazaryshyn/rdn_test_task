from dataclasses import dataclass


@dataclass
class PricePerHour:
    date_of_parsing: str
    hour: int
    price: float
    sales_volume_MWh: float
    purchase_volume_MWh: float
    declared_sales_volume_MWh: float
    declared_purchase_volume_MWh: float
