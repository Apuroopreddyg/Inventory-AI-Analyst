from langchain.tools import tool
from database.mongodb import db
from datetime import datetime
from uuid import uuid4

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
            "product": item["name"],
            "stock": item["stock"],
            "reorderLevel": item["reorderLevel"],
            "vendor": item["vendor"]
        }
        for item in products
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
    
@tool
def reorder_inventory(product: str, quantity: int) -> str:
    """Create a purchase order for a specified product and quantity."""

    # Find the product in MongoDB
    product_data = db["products"].find_one({
        "name": {
            "$regex": f"^{product}$",
            "$options": "i"
        }
    })

    if not product_data:
        return f"Error: Product '{product}' was not found in inventory."

    # Generate a unique purchase order number
    po_number = f"PO-{uuid4().hex[:8].upper()}"

    # Create purchase order / delivery document
    purchase_order = {
        "poNumber": po_number,
        "vendor": product_data["vendor"],
        "product": product_data["name"],
        "quantity": quantity,
        "status": "Pending",
        "createdAt": datetime.utcnow()
    }

    # Save to MongoDB deliveries collection
    db["deliveries"].insert_one(purchase_order)

    return (
        f"Purchase order created successfully. "
        f"PO Number: {po_number}. "
        f"Product: {product_data['name']}. "
        f"Quantity: {quantity}. "
        f"Vendor: {product_data['vendor']}. "
        f"Status: Pending."
    )


@tool
def receive_delivery(po_number: str) -> str:
    """Receive a pending purchase order and update inventory stock."""

    # Find the purchase order
    delivery = db["deliveries"].find_one({
        "poNumber": po_number,
        "status": "Pending"
    })

    if not delivery:
        return (
            f"Pending purchase order {po_number} "
            "was not found."
        )

    product_name = delivery["product"]
    quantity = delivery["quantity"]

    # Increase stock only when goods are received
    result = db["products"].update_one(
        {"name": product_name},
        {"$inc": {"stock": quantity}}
    )

    if result.matched_count == 0:
        return f"Product '{product_name}' was not found in inventory."

    # Mark the purchase order as delivered
    db["deliveries"].update_one(
        {"_id": delivery["_id"]},
        {
            "$set": {
                "status": "Delivered",
                "receivedAt": datetime.utcnow()
            }
        }
    )

    # Record the stock receipt transaction
    db["inventory_transactions"].insert_one({
        "product": product_name,
        "quantity": quantity,
        "type": "IN",
        "vendor": delivery["vendor"],
        "date": datetime.utcnow(),
        "poNumber": po_number
    })

    return (
        f"Delivery received successfully. "
        f"PO: {po_number}. "
        f"Product: {product_name}. "
        f"Quantity received: {quantity}. "
        f"Stock updated."
    )

@tool
def generate_inventory_report() -> str:
    """Generate a complete inventory report including low-stock products,
    pending deliveries, and inventory received this month."""
        
    from agent.inventory_report_workflow import inventory_report_workflow

    initial_state = {
        "low_stock": [],
        "pending_deliveries": [],
        "monthly_received": [],
        "report": ""
    }

    result = inventory_report_workflow.invoke(initial_state)

    return result["report"]