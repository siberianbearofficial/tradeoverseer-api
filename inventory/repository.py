from utils.repository import SQLAlchemyRepository

from inventory.models import InventoryItem


class InventoryRepository(SQLAlchemyRepository):
    model = InventoryItem
