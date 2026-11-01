from database.mongodb import db

deliveries = [
    {
        "vendor": "Cisco",
        "product": "Router",
        "quantity": 100,
        "status": "Pending"
    },
    {
        "vendor": "Fortinet",
        "product": "Firewall",
        "quantity": 50,
        "status": "Delivered"
    },
    {
        "vendor": "Juniper",
        "product": "Switch",
        "quantity": 75,
        "status": "Pending"
    }
]

result = db.deliveries.insert_many(deliveries)

print("Inserted delivery IDs:", result.inserted_ids)