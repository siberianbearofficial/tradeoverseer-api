from uuid import UUID

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from utils.exceptions import exception_handler
from utils.dependency import (RaritiesServiceDep,
                              AuthenticationDep,
                              RolesServiceDep,
                              UOWDep,
                              AuthenticationServiceDep)

from authentication.exceptions import NotAuthenticatedError

from rarities.exceptions import *
from rarities.schemas import RarityCreate, RarityUpdate

router = APIRouter(prefix='/rarities', tags=['Rarities'])


@router.get('')
@cache(namespace='rarities', expire=3600)
@exception_handler
async def get_rarities_handler(rarities_service: RaritiesServiceDep,
                               authentication_service: AuthenticationServiceDep,
                               roles_service: RolesServiceDep,
                               uow: UOWDep,
                               name: str | None = None,
                               authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_rarities')
    if not can_read:
        raise ReadRarityDenied

    rarities = await rarities_service.get_rarities(uow, name=name)
    return {
        'data': rarities,
        'detail': 'Rarities were selected.'
    }


@router.get('/{uuid}')
@cache(namespace='rarities', expire=3600)
@exception_handler
async def get_rarity_handler(rarities_service: RaritiesServiceDep,
                             authentication_service: AuthenticationServiceDep,
                             roles_service: RolesServiceDep,
                             uow: UOWDep,
                             uuid: UUID,
                             authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_rarities')
    if not can_read:
        raise ReadRarityDenied

    rarity = await rarities_service.get_rarity(uow, uuid)
    if not rarity:
        raise RarityNotFoundError

    return {
        'data': rarity,
        'detail': 'Rarity was selected.'
    }


@router.post('/')
@exception_handler
async def post_rarity_handler(uow: UOWDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              rarities_service: RaritiesServiceDep,
                              rarity: RarityCreate,
                              authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_insert = await roles_service.has_permission(uow, author, 'insert_rarities')
    if not can_insert:
        raise InsertRarityDenied

    await rarities_service.add_rarity(uow, rarity)
    await FastAPICache.clear(namespace='rarities')
    await FastAPICache.clear(namespace='skins')
    return {
        'data': None,
        'detail': 'Rarity was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def put_rarity_handler(uow: UOWDep,
                             authentication_service: AuthenticationServiceDep,
                             roles_service: RolesServiceDep,
                             rarities_service: RaritiesServiceDep,
                             uuid: UUID,
                             rarity: RarityUpdate,
                             authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    rarity_with_this_uuid = await rarities_service.get_rarity(uow, uuid)
    if not rarity_with_this_uuid:
        raise RarityNotFoundError

    can_update = await roles_service.has_permission(uow, author, 'update_rarities')
    if not can_update:
        raise UpdateRarityDenied

    await rarities_service.update_rarity(uow, uuid, rarity)
    await FastAPICache.clear(namespace='rarities')
    await FastAPICache.clear(namespace='skins')
    return {
        'data': None,
        'detail': 'Rarity was updated.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_rarity_handler(uow: UOWDep,
                                authentication_service: AuthenticationServiceDep,
                                roles_service: RolesServiceDep,
                                rarities_service: RaritiesServiceDep,
                                uuid: UUID,
                                authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    rarity_with_this_uuid = await rarities_service.get_rarity(uow, uuid)
    if not rarity_with_this_uuid:
        raise RarityNotFoundError

    can_delete = await roles_service.has_permission(uow, author, 'delete_rarities')
    if not can_delete:
        raise DeleteRarityDenied

    await rarities_service.delete_rarity(uow, uuid)
    await FastAPICache.clear(namespace='rarities')
    await FastAPICache.clear(namespace='skins')
    return {
        'data': None,
        'detail': 'Rarity was deleted.'
    }
