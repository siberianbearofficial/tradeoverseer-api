from pydantic import BaseModel
from uuid import UUID


class RarityRead(BaseModel):
    uuid: UUID
    name: str
    color: str

    class Config:
        from_attributes = True


class RarityCreate(BaseModel):
    name: str
    color: str


class RarityUpdate(BaseModel):
    name: str
    color: str
