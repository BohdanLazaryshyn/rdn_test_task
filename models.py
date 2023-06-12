from config import db


class PricePerHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_parsing = db.Column(db.String(10), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sales_volume_MWh = db.Column(db.Float, nullable=False)
    purchase_volume_MWh = db.Column(db.Float, nullable=False)
    declared_sales_volume_MWh = db.Column(db.Float, nullable=False)
    declared_purchase_volume_MWh = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "date_of_parsing": self.date_of_parsing,
            "hour": self.hour,
            "price": self.price,
            "sales_volume_MWh": self.sales_volume_MWh,
            "purchase_volume_MWh": self.purchase_volume_MWh,
            "declared_sales_volume_MWh": self.declared_sales_volume_MWh,
            "declared_purchase_volume_MWh": self.declared_purchase_volume_MWh,
        }
