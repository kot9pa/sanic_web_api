from enum import Enum
from typing import Annotated
from annotated_types import MinLen
from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    user = "user"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(3)]


class UserCreate(UserBase):
    fullname: str | None = None
    role: Role


class UserUpdate(UserCreate):
    pass


# class UserUpdatePartial(UserView):
#     email: EmailStr | None = None
#     password: Annotated[str, MinLen(3)] | None = None
#     fullname: str | None = None
#     role: Role | None = None
