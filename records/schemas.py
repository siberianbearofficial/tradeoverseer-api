from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class RecordRead(BaseModel):
    uuid: UUID
    registered_at: datetime
    skin_uuid: UUID
    price: str
    count: int
    labels: list[str] | None = None

    class Config:
        from_attributes = True


class RecordCreate(BaseModel):
    skin_uuid: UUID
    price: str
    count: int

    class Config:
        from_attributes = True


class RecordUpdate(BaseModel):
    registered_at: datetime | None = None
    skin_uuid: UUID | None = None
    price: str | None = None
    count: int | None = None


class RealtimeRecordRead(BaseModel):
    skin_uuid: UUID
    previous_price: str | None = None
    last_price: str
    previous_count: int | None = None
    last_count: int

    class Config:
        from_attributes = True
