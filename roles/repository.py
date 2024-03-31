from utils.repository import SQLAlchemyRepository

from roles.models import Role


class RolesRepository(SQLAlchemyRepository):
    model = Role
