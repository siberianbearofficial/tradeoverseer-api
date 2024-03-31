from uuid import uuid4
from datetime import datetime
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, Integer, String, Uuid)
from utils.database import Base

from skins.models import Skin

from records.schemas import RecordRead, RealtimeRecordRead


class Record(Base):
    __tablename__ = "record"

    uuid = Column(Uuid, primary_key=True, default=uuid4)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    skin_uuid = Column(Uuid, ForeignKey(Skin.uuid))
    price = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    labels = Column(String, nullable=False)

    def to_read_model(self) -> RecordRead:
        return RecordRead(
            uuid=self.uuid,
            registered_at=self.registered_at,
            skin_uuid=self.skin_uuid,
            price=self.price,
            count=self.count,
            labels=self.labels
        )


class RealtimeRecord(Base):
    __tablename__ = "realtime_record"

    skin_uuid = Column(Uuid, ForeignKey(Skin.uuid), primary_key=True, nullable=False)
    previous_price = Column(String, nullable=True)
    last_price = Column(String, nullable=False)
    previous_count = Column(Integer, nullable=True)
    last_count = Column(Integer, nullable=False)

    def to_read_model(self) -> RealtimeRecordRead:
        return RealtimeRecordRead(
            skin_uuid=self.skin_uuid,
            previous_price=self.previous_price,
            last_price=self.last_price,
            previous_count=self.previous_count,
            last_count=self.last_count
        )
