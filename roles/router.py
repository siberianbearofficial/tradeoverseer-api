from uuid import UUID

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from utils.exceptions import exception_handler
from utils.dependency import (AuthenticationServiceDep,
                              RolesServiceDep,
                              AuthenticationDep,
                              UOWDep)

from authentication.exceptions import NotAuthenticatedError

from roles.schemas import RoleCreate, RoleUpdate
from roles.exceptions import *

router = APIRouter(prefix='/roles', tags=['Roles'])


@router.get('')
@cache(namespace='roles', expire=3600)
@exception_handler
async def get_roles_handler(roles_service: RolesServiceDep,
                            authentication_service: AuthenticationServiceDep,
                            uow: UOWDep,
                            name: str | None = None,
                            authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_roles')
    if not can_read:
        raise ReadRoleDenied

    roles = await roles_service.get_roles(uow, name=name)
    return {
        'data': roles,
        'detail': 'Roles were selected.'
    }


@router.get('/{uuid}')
@cache(namespace='roles', expire=3600)
@exception_handler
async def get_role_handler(authentication_service: AuthenticationServiceDep,
                           roles_service: RolesServiceDep,
                           uow: UOWDep,
                           uuid: UUID,
                           authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_roles')
    if not can_read:
        raise ReadRoleDenied

    role = await roles_service.get_role(uow, uuid)
    if not role:
        raise RoleNotFoundError

    return {
        'data': role,
        'detail': 'Role was selected.'
    }


@router.post('/')
@exception_handler
async def post_role_handler(uow: UOWDep,
                            authentication_service: AuthenticationServiceDep,
                            roles_service: RolesServiceDep,
                            role: RoleCreate,
                            authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_insert = await roles_service.has_permission(uow, author, 'insert_roles')
    if not can_insert:
        raise InsertRoleDenied

    await roles_service.add_role(uow, role)
    await FastAPICache.clear(namespace='roles')
    await FastAPICache.clear(namespace='users')
    return {
        'data': None,
        'detail': 'Role was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def put_role_handler(uow: UOWDep,
                           authentication_service: AuthenticationServiceDep,
                           roles_service: RolesServiceDep,
                           uuid: UUID,
                           role: RoleUpdate,
                           authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    role_with_this_uuid = await roles_service.get_role(uow, uuid)
    if not role_with_this_uuid:
        raise RoleNotFoundError

    can_update = await roles_service.has_permission(uow, author, 'update_roles')
    if not can_update:
        raise UpdateRoleDenied

    await roles_service.update_role(uow, uuid, role)
    await FastAPICache.clear(namespace='roles')
    await FastAPICache.clear(namespace='users')
    return {
        'data': None,
        'detail': 'Role was updated.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_role_handler(uow: UOWDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              uuid: UUID,
                              authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    role_with_this_uuid = await roles_service.get_role(uow, uuid)
    if not role_with_this_uuid:
        raise RoleNotFoundError

    can_delete = await roles_service.has_permission(uow, author, 'delete_roles')
    if not can_delete:
        raise DeleteRoleDenied

    await roles_service.delete_role(uow, uuid)
    await FastAPICache.clear(namespace='roles')
    await FastAPICache.clear(namespace='users')
    return {
        'data': None,
        'detail': 'Role was deleted.'
    }
