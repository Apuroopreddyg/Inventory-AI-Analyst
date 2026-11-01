from database.mongodb import db

products = [
    {
        "name": "Router",
        "category": "Networking",
        "stock": 25,
        "reorderLevel": 50,
        "price": 5000,
        "vendor": "Cisco"
    },
    {
        "name": "Firewall",
        "category": "Security",
        "stock": 10,
        "reorderLevel": 30,
        "price": 15000,
        "vendor": "Fortinet"
    },
    {
        "name": "Switch",
        "category": "Networking",
        "stock": 100,
        "reorderLevel": 40,
        "price": 8000,
        "vendor": "Juniper"
    }
]

result = db.products.insert_many(products)

print("Inserted product IDs:", result.inserted_ids)