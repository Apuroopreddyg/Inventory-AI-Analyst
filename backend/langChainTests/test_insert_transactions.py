from database.mongodb import db
from datetime import datetime

transactions = [
    {
        "product": "Router",
        "quantity": 100,
        "type": "IN",
        "vendor": "Cisco",
        "date": datetime(2026, 10, 10)
    },
    {
        "product": "Switch",
        "quantity": 50,
        "type": "IN",
        "vendor": "Juniper",
        "date": datetime(2026, 10, 15)
    },
    {
        "product": "Firewall",
        "quantity": 20,
        "type": "OUT",
        "vendor": "Internal",
        "date": datetime(2026, 10, 20)
    },
    {
        "product": "Router",
        "quantity": 30,
        "type": "IN",
        "vendor": "Cisco",
        "date": datetime(2026, 9, 25)
    }
]

result = db.inventory_transactions.insert_many(transactions)

print("Inserted transaction IDs:", result.inserted_ids)