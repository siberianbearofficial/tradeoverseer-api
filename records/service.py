from uuid import UUID, uuid4
from datetime import datetime, timedelta
from json import dumps, loads

from utils.unitofwork import IUnitOfWork
from utils.config import INSERT_ACCESS_KEY

from records.repository import *
from records.schemas import RecordCreate, RecordUpdate
from records.logic import days_in_year, days_in_month


class RecordsService:
    def __init__(self, records_repository: RecordsRepository,
                 realtime_records_repository: RealtimeRecordsRepository):
        self.records_repository = records_repository
        self.realtime_records_repository = realtime_records_repository

    async def get_records(self, uow: IUnitOfWork, skin_uuid: UUID, period: str, year_offset: int | None = None):
        async with uow:
            now = datetime.now(tz=None)
            now_days_in_year = days_in_year(now.year)
            now_days_in_month = days_in_month(now.year, now.month)
            period = period.strip().lower()
            if period == 'year':
                if year_offset is not None:
                    records = await self.records_repository.find_all(uow.session, {
                        'registered_at': ('between', now - (year_offset + 1) * timedelta(days=now_days_in_year),
                                          now - year_offset * timedelta(days=now_days_in_year))
                    }, skin_uuid=skin_uuid)
                else:
                    records = await self.records_repository.find_all(uow.session, {
                        'registered_at': ('between', now - timedelta(days=now_days_in_year), now)
                    }, skin_uuid=skin_uuid)
                records = list(filter(lambda record: 'year' in loads(record.labels), records))
            elif period == 'month':
                records = await self.records_repository.find_all(uow.session, {
                    'registered_at': ('between', now - timedelta(days=now_days_in_month), now)
                }, skin_uuid=skin_uuid)
                records = list(filter(lambda record: 'month' in loads(record.labels), records))
            else:
                records = await self.records_repository.find_all(uow.session, {
                    'registered_at': ('between', now - timedelta(days=1), now)
                }, skin_uuid=skin_uuid)
                records = list(filter(lambda record: 'day' in loads(record.labels), records))
            return records

    async def get_record(self, uow: IUnitOfWork, uuid: UUID, skin_uuid: UUID | None = None, realtime: bool = False):
        async with uow:
            if realtime:
                record = await self.realtime_records_repository.find_one(uow.session, skin_uuid=skin_uuid)
            else:
                record = await self.records_repository.find_one(uow.session, uuid=uuid)
            return record

    async def add_record(self, uow: IUnitOfWork, record: RecordCreate):
        async with uow:
            # Проверяем, какие лейблы нужно навесить новой записи.
            # Т.е. проверяем, является ли запись первой за последние день, два часа и пятнадцать минут.
            now = datetime.now(tz=None)

            labels = list()

            day_records = await self.records_repository.find_all(uow.session, {
                'registered_at': ('between', now - timedelta(days=1), now)
            }, skin_uuid=record.skin_uuid)
            day_records = list(filter(lambda rec: 'day' in loads(rec.labels), day_records))
            if not day_records:
                labels.append('year')

            two_hours_records = await self.records_repository.find_all(uow.session, {
                'registered_at': ('between', now - timedelta(hours=2), now)
            }, skin_uuid=record.skin_uuid)
            two_hours_records = list(filter(lambda rec: 'day' in loads(rec.labels), two_hours_records))
            if not two_hours_records:
                labels.append('month')

            fifteen_minutes_records = await self.records_repository.find_all(uow.session, {
                'registered_at': ('between', now - timedelta(minutes=15), now)
            }, skin_uuid=record.skin_uuid)
            fifteen_minutes_records = list(filter(lambda rec: 'day' in loads(rec.labels), fifteen_minutes_records))
            if not fifteen_minutes_records:
                labels.append('day')

            # Сохраняем запись в базу
            record_dict = {
                'uuid': uuid4(),
                'registered_at': now,
                'skin_uuid': record.skin_uuid,
                'price': record.price,
                'count': record.count,
                'labels': dumps(labels)
            }
            await self.records_repository.add_one(uow.session, record_dict)

            # Обновляем значение цены в реальном времени (отдельная таблица)
            prev_realtime_record = await self.realtime_records_repository.find_one(uow.session,
                                                                                   skin_uuid=record_dict['skin_uuid'])
            if prev_realtime_record:
                realtime_record_dict = {
                    'previous_price': prev_realtime_record.last_price,
                    'last_price': record.price,
                    'previous_count': prev_realtime_record.last_count,
                    'last_count': record.count
                }
                await self.realtime_records_repository.edit_one(uow.session, record_dict['skin_uuid'],
                                                                realtime_record_dict)
            else:
                realtime_record_dict = {
                    'skin_uuid': record_dict['skin_uuid'],
                    'previous_price': prev_realtime_record.last_price,
                    'last_price': record.price,
                    'previous_count': prev_realtime_record.last_count,
                    'last_count': record.count
                }
                await self.realtime_records_repository.add_one(uow.session, realtime_record_dict)

            await uow.commit()

    async def update_record(self, uow: IUnitOfWork, uuid: UUID, record: RecordUpdate):
        async with uow:
            record_dict = dict()
            if record.registered_at:
                record_dict['registered_at'] = record.registered_at.replace(tzinfo=None)
            if record.skin_uuid:
                record_dict['skin_uuid'] = record.skin_uuid
            if record.price:
                record_dict['price'] = record.price
            if record.count is not None:
                record_dict['count'] = record.count

            await self.records_repository.edit_one(uow.session, uuid, record_dict)
            await uow.commit()

    async def delete_record(self, uow: IUnitOfWork, uuid: UUID):
        async with uow:
            await self.records_repository.delete_one(uow.session, uuid)
            await uow.commit()

    @staticmethod
    def has_insert_access(insert_access: str | None = None):
        if insert_access:
            if insert_access.strip() == INSERT_ACCESS_KEY.strip():
                return True
        return False
