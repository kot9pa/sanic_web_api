from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    balance: int = Field(default=0)


class AccountCreate(AccountBase):
    user_id: int
