from fastapi import APIRouter

from utils.logic import check_password
from utils.exceptions import exception_handler
from utils.dependency import UsersServiceDep, UOWDep

from users.exceptions import UserNotFoundError

from authentication.schemas import Authentication
from authentication.exceptions import IncorrectCredentialsError
from authentication.logic import *

router = APIRouter(prefix='/authentication', tags=['Authentication'])


@router.post('')
@exception_handler
async def post_sign_in_handler(users_service: UsersServiceDep,
                               uow: UOWDep,
                               authentication: Authentication):
    users = await users_service.get_users(uow, username=authentication.username, with_password=True)
    if not users:
        raise UserNotFoundError

    if not check_password(authentication.password, users[0].hashed_password):
        raise IncorrectCredentialsError

    payload = await get_payload(users[0].uuid, users[0].roles)
    return payload
