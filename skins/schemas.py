from pydantic import BaseModel
from uuid import UUID


class SkinRead(BaseModel):
    uuid: UUID
    name: str
    rarity_uuid: UUID

    class Config:
        from_attributes = True


class SkinCreate(BaseModel):
    name: str
    rarity_uuid: UUID


class SkinUpdate(BaseModel):
    name: str
    rarity_uuid: UUID
