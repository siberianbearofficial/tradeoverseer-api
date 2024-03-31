from utils.repository import SQLAlchemyRepository

from records.models import Record, RealtimeRecord


class RecordsRepository(SQLAlchemyRepository):
    model = Record


class RealtimeRecordsRepository(SQLAlchemyRepository):
    model = RealtimeRecord
