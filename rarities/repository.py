from utils.repository import SQLAlchemyRepository

from rarities.models import Rarity


class RaritiesRepository(SQLAlchemyRepository):
    model = Rarity
