from langchain.tools import tool
from database.mongodb import db
from datetime import datetime

@tool
def get_low_stock_items():
    """Returns products whose stock is below their reorder level."""

    products = db.products.find({
        "$expr": {
            "$lt": ["$stock", "$reorderLevel"]
        }
    })

    return [
        {
            "name": product["name"],
            "stock": product["stock"],
            "reorderLevel": product["reorderLevel"]
        }
        for product in products
    ]


@tool
def get_pending_deliveries():
    """Returns all vendors with pending deliveries."""

    deliveries = db.deliveries.find({
        "status": "Pending"
    })

    return [
        {
            "vendor": delivery["vendor"],
            "status": delivery["status"]
        }
        for delivery in deliveries
    ]


@tool
def get_monthly_inventory():
    """Returns inventory received during the current month."""

    now = datetime.now()

    start_of_month = datetime(
        now.year,
        now.month,
        1
    )

    if now.month == 12:
        start_of_next_month = datetime(
            now.year + 1,
            1,
            1
        )
    else:
        start_of_next_month = datetime(
            now.year,
            now.month + 1,
            1
        )

    transactions = db.inventory_transactions.find({
        "type": "IN",
        "date": {
            "$gte": start_of_month,
            "$lt": start_of_next_month
        }
    })

    return [
        {
            "product": item["product"],
            "quantity": item["quantity"],
            "vendor": item["vendor"]
        }
        for item in transactions
    ]