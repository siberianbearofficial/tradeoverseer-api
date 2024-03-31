from utils.repository import SQLAlchemyRepository

from skins.models import Skin


class SkinsRepository(SQLAlchemyRepository):
    model = Skin
