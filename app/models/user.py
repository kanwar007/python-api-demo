from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)


class UserRead(UserCreate):
    id: int