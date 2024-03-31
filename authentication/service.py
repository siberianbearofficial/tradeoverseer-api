import jwt

from users.repository import UsersRepository

from utils.unitofwork import IUnitOfWork
from utils.config import AUTH_SECRET


class AuthenticationService:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    async def authenticated_user(self, uow: IUnitOfWork, authorization: str | None):
        async with uow:
            if not authorization:
                return

            token = authorization.split()
            if len(token) <= 1:
                return

            token = token[1].strip()
            payload = jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
            uuid = payload['sub']

            if not uuid:
                return

            user = await self.users_repository.find_one(uow.session, uuid=uuid)
            return user
