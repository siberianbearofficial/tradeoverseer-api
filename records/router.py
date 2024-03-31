from uuid import UUID

from fastapi import APIRouter

from utils.exceptions import exception_handler
from utils.dependency import (RecordsServiceDep,
                              AuthenticationServiceDep,
                              RolesServiceDep,
                              SkinsServiceDep,
                              AuthenticationDep,
                              InsertAccessKeyDep,
                              UOWDep)

from authentication.exceptions import NotAuthenticatedError
from skins.exceptions import SkinNotFoundError

from records.schemas import RecordCreate, RecordUpdate
from records.logic import *
from records.exceptions import *

router = APIRouter(prefix='/records', tags=['Records'])


@router.get('')
@exception_handler
async def get_records_handler(records_service: RecordsServiceDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              uow: UOWDep,
                              skin_uuid: UUID,
                              period: str,
                              year_offset: int | None = None,
                              authorization: AuthenticationDep = None):
    validate_period(period)
    if year_offset is not None:
        validate_year_offset(year_offset)

    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_records')
    if not can_read:
        raise ReadRecordDenied

    records = await records_service.get_records(uow, skin_uuid=skin_uuid, period=period, year_offset=year_offset)

    return {
        'data': records,
        'detail': 'Records were selected.'
    }


@router.get('/realtime')
@exception_handler
async def get_record_handler(records_service: RecordsServiceDep,
                             authentication_service: AuthenticationServiceDep,
                             roles_service: RolesServiceDep,
                             uow: UOWDep,
                             skin_uuid: UUID,
                             authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_records')
    if not can_read:
        raise ReadRecordDenied

    record = await records_service.get_record(uow, skin_uuid=skin_uuid, realtime=True)
    if not record:
        raise RecordNotFoundError

    return {
        'data': record,
        'detail': 'Record was selected.'
    }


@router.get('/{uuid}')
@exception_handler
async def get_record_handler(records_service: RecordsServiceDep,
                             authentication_service: AuthenticationServiceDep,
                             roles_service: RolesServiceDep,
                             uow: UOWDep,
                             uuid: UUID,
                             authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_read = await roles_service.has_permission(uow, author, 'read_records')
    if not can_read:
        raise ReadRecordDenied

    record = await records_service.get_record(uow, uuid)
    if not record:
        raise RecordNotFoundError

    return {
        'data': record,
        'detail': 'Record was selected.'
    }


@router.post('/')
@exception_handler
async def post_records_handler(record: RecordCreate,
                               records_service: RecordsServiceDep,
                               authentication_service: AuthenticationServiceDep,
                               roles_service: RolesServiceDep,
                               skins_service: SkinsServiceDep,
                               uow: UOWDep,
                               insert_access_key: InsertAccessKeyDep = None,
                               authorization: AuthenticationDep = None):
    validate_price(record.price)
    validate_count(record.count)

    author = await authentication_service.authenticated_user(uow, authorization)
    can_insert = False
    if author:
        can_insert = await roles_service.has_permission(uow, author, 'insert_records')
    if not can_insert:
        can_insert = records_service.has_insert_access(insert_access_key)
    if not can_insert:
        raise InsertRecordDenied

    skin_with_this_uuid = await skins_service.get_skin(uow, record.skin_uuid)
    if not skin_with_this_uuid:
        raise SkinNotFoundError

    await records_service.add_record(uow, record)
    return {
        'data': None,
        'detail': 'Record was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def put_records_handler(record: RecordUpdate,
                              records_service: RecordsServiceDep,
                              authentication_service: AuthenticationServiceDep,
                              roles_service: RolesServiceDep,
                              skins_service: SkinsServiceDep,
                              uow: UOWDep,
                              uuid: UUID,
                              authorization: AuthenticationDep = None):
    if record.price:
        validate_price(record.price)
    if record.count is not None:
        validate_count(record.count)

    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_update = await roles_service.has_permission(uow, author, 'update_records')
    if not can_update:
        raise UpdateRecordDenied

    record_with_this_uuid = await records_service.get_record(uow, uuid)
    if not record_with_this_uuid:
        raise RecordNotFoundError

    if record.skin_uuid:
        skin_with_this_uuid = await skins_service.get_skin(uow, record.skin_uuid)
        if not skin_with_this_uuid:
            raise SkinNotFoundError

    await records_service.update_record(uow, uuid, record)
    return {
        'data': None,
        'detail': 'Record was updated.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_record_handler(records_service: RecordsServiceDep,
                                authentication_service: AuthenticationServiceDep,
                                roles_service: RolesServiceDep,
                                uow: UOWDep,
                                uuid: UUID,
                                authorization: AuthenticationDep = None):
    author = await authentication_service.authenticated_user(uow, authorization)
    if not author:
        raise NotAuthenticatedError

    can_delete = await roles_service.has_permission(uow, author, 'delete_records')
    if not can_delete:
        raise DeleteRecordDenied

    record = await records_service.get_record(uow, uuid)
    if not record:
        raise RecordNotFoundError

    await records_service.delete_record(uow, uuid)
    return {
        'data': None,
        'detail': 'Record was deleted.'
    }
