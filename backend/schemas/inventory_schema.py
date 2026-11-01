
from pydantic import BaseModel, Field


class LowStockItem(BaseModel):
    product: str
    stock: int
    reorder_level: int
    status: str


class PendingDelivery(BaseModel):
    vendor: str
    status: str


class ReceivedInventory(BaseModel):
    product: str
    quantity: int
    vendor: str


class InventoryReport(BaseModel):

    low_stock_items: list[LowStockItem] = Field(
        description="Products below their reorder level"
    )

    pending_deliveries: list[PendingDelivery] = Field(
        description="Deliveries that have not yet been completed"
    )

    received_inventory: list[ReceivedInventory] = Field(
        description="Inventory received during the current month"
    )

    summary: str = Field(
        description="A brief summary of the inventory situation"
    )
