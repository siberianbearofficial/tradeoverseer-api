from pydantic import BaseModel
from uuid import UUID


class RoleRead(BaseModel):
    uuid: UUID
    name: str
    permissions: list[str]

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    permissions: list[str]


class RoleUpdate(BaseModel):
    name: str
    permissions: list[str]
