from uuid import UUID

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from utils.logic import equal_uuids
from utils.exceptions import exception_handler
from utils.dependency import (SkinsServiceDep,
                              AuthenticationDep,
                              RolesServiceDep,
                              UOWDep,
                              AuthenticationServiceDep)

from authentication.exceptions import NotAuthenticatedError

from skins.exceptions import *
from skins.schemas import SkinCreate, SkinUpdate

router = APIRouter(prefix='/skins', tags=['Skins'])


@router.get('')
@cache(namespace='skins', expire=3600)
@exception_handler
async def get_skins_handler(skins_service: SkinsServiceDep,
                            authentication_service: AuthenticationServiceDep,
                            roles_service: RolesServiceDep,
                            uow: UOWDep,
                            name: str | None = None,
                            authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_skins')
    if not can_read:
        raise ReadSkinDenied

    skins = await skins_service.get_skins(uow, name=name)
    return {
        'data': skins,
        'detail': 'Skins were selected.'
    }


@router.get('/{uuid}')
@cache(namespace='skins', expire=3600)
@exception_handler
async def get_skin_handler(skins_service: SkinsServiceDep,
                           authentication_service: AuthenticationServiceDep,
                           roles_service: RolesServiceDep,
                           uow: UOWDep,
                           uuid: UUID,
                           authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_skins')
    if not can_read:
        raise ReadSkinDenied

    skin = await skins_service.get_skin(uow, uuid)
    if not skin:
        raise SkinNotFoundError

    return {
        'data': skin,
        'detail': 'Skin was selected.'
    }


@router.post('/')
@exception_handler
async def post_skin_handler(uow: UOWDep,
                            authentication_service: AuthenticationServiceDep,
                            roles_service: RolesServiceDep,
                            skins_service: SkinsServiceDep,
                            uuid: UUID,
                            skin: SkinCreate,
                            authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_insert = await roles_service.has_permission(uow, author, 'insert_skins')
    if not can_insert:
        raise InsertSkinDenied

    await skins_service.add_skin(uow, skin)
    await FastAPICache.clear(namespace='skins')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'Skin was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def put_skin_handler(uow: UOWDep,
                           authentication_service: AuthenticationServiceDep,
                           roles_service: RolesServiceDep,
                           skins_service: SkinsServiceDep,
                           uuid: UUID,
                           skin: SkinUpdate,
                           authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    skin_with_this_uuid = await skins_service.get_skin(uow, uuid)
    if not skin_with_this_uuid:
        raise SkinNotFoundError

    can_update = await roles_service.has_permission(uow, author, 'update_skins')
    if not can_update:
        raise UpdateSkinDenied

    await skins_service.update_skin(uow, uuid, skin)
    await FastAPICache.clear(namespace='skins')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'Skin was updated.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_skin_handler(uow: UOWDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              skins_service: SkinsServiceDep,
                              uuid: UUID,
                              authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    skin_with_this_uuid = await skins_service.get_skin(uow, uuid)
    if not skin_with_this_uuid:
        raise SkinNotFoundError

    can_delete = await roles_service.has_permission(uow, author, 'delete_skins')
    if not can_delete:
        raise DeleteSkinDenied

    await skins_service.delete_skin(uow, uuid)
    await FastAPICache.clear(namespace='skins')
    await FastAPICache.clear(namespace='inventory')
    return {
        'data': None,
        'detail': 'Skin was deleted.'
    }
