from pydantic import BaseModel


class Authentication(BaseModel):
    username: str
    password: str
