from pydantic import BaseModel


class TransactionBase(BaseModel):
    amount: int
    signature: str
    transaction_id: str
    user_id: int
    account_id: int


class TransactionCreate(TransactionBase):
    pass
