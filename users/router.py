from uuid import UUID

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from utils.logic import equal_uuids, check_password
from utils.exceptions import exception_handler
from utils.dependency import (UsersServiceDep,
                              AuthenticationServiceDep,
                              InventoryServiceDep,
                              RolesServiceDep,
                              AuthenticationDep,
                              UOWDep)

from authentication.exceptions import NotAuthenticatedError, IncorrectCredentialsError
from roles.exceptions import RoleNotFoundError

from users.schemas import UserCreate, UserUpdate, ChangePassword
from users.exceptions import *
from users.logic import validate_username, validate_password

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('')
@cache(namespace='users', expire=3600)
@exception_handler
async def get_users_handler(users_service: UsersServiceDep,
                            uow: UOWDep,
                            username: str | None = None):
    users = await users_service.get_users(uow, username=username)
    return {
        'data': users,
        'detail': 'Users were selected.'
    }


@router.get('/{uuid}')
@cache(namespace='users', expire=3600)
@exception_handler
async def get_user_handler(users_service: UsersServiceDep,
                           uow: UOWDep,
                           uuid: UUID):
    user = await users_service.get_user(uow, uuid)
    if not user:
        raise UserNotFoundError

    return {
        'data': user,
        'detail': 'User was selected.'
    }


@router.post('/')
@exception_handler
async def post_users_handler(users_service: UsersServiceDep,
                             authentication_service: AuthenticationServiceDep,
                             roles_service: RolesServiceDep,
                             uow: UOWDep,
                             user: UserCreate,
                             authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    validate_username(user.username)
    validate_password(user.password)

    users_with_same_usernames = await users_service.get_users(uow, username=user.username)
    if users_with_same_usernames:
        raise UsernameTakenError

    can_insert = await roles_service.has_permission(uow, author, 'insert_users')
    if not can_insert:
        raise InsertUserDenied

    fake_role = await roles_service.get_fake_role(uow, user.roles)
    if fake_role:
        raise RoleNotFoundError

    await users_service.add_user(uow, user)
    await FastAPICache.clear(namespace='users')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'User was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def put_users_handler(users_service: UsersServiceDep,
                            authentication_service: AuthenticationServiceDep,
                            roles_service: RolesServiceDep,
                            uow: UOWDep,
                            uuid: UUID,
                            user: UserUpdate,
                            authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    validate_username(user.username)

    can_update = False
    if not equal_uuids(author.uuid, uuid):
        can_update = await roles_service.has_permission(uow, author, 'update_users')
        if not can_update:
            raise UpdateUserDenied

    users_with_new_username = await users_service.get_users(uow, username=user.username)
    if users_with_new_username and not equal_uuids(users_with_new_username[0].uuid, uuid):
        raise UsernameTakenError

    if can_update:
        fake_role = await roles_service.get_fake_role(uow, user.roles)
        if fake_role:
            raise RoleNotFoundError

        await users_service.update_user(uow, uuid, user, full_update=True)
    else:
        await users_service.update_user(uow, uuid, user)
    await FastAPICache.clear(namespace='users')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'User was updated.'
    }


@router.put('/{uuid}/password')
@exception_handler
async def put_users_password_handler(users_service: UsersServiceDep,
                                     authentication_service: AuthenticationServiceDep,
                                     uow: UOWDep,
                                     uuid: UUID,
                                     change_password: ChangePassword,
                                     authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    if not equal_uuids(author.uuid, uuid):
        raise ChangePasswordDenied

    validate_password(change_password.new_password)

    user_with_this_uuid = await users_service.get_user(uow, uuid, with_password=True)
    if not user_with_this_uuid:
        raise UserNotFoundError

    if not check_password(change_password.current_password, user_with_this_uuid.hashed_password):
        raise IncorrectCredentialsError

    await users_service.change_password(uow, uuid, change_password)
    await FastAPICache.clear(namespace='users')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'Password was changed.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_user_handler(users_service: UsersServiceDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              inventory_service: InventoryServiceDep,
                              uow: UOWDep,
                              uuid: UUID,
                              authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    user_with_this_uuid = await users_service.get_user(uow, uuid)
    if not user_with_this_uuid:
        raise UserNotFoundError

    if not equal_uuids(author.uuid, user_with_this_uuid.uuid):
        can_delete = await roles_service.has_permission(uow, author, 'delete_users')
        if not can_delete:
            raise DeleteUserDenied

    await inventory_service.delete_inventory_items(uow, user_with_this_uuid.uuid)
    await users_service.delete_user(uow, user_with_this_uuid.uuid)
    await FastAPICache.clear(namespace='users')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'User was deleted.'
    }
