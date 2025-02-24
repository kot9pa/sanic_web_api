from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.base import Base


if TYPE_CHECKING:
    from src.api_v1.users.models import User
    from src.api_v1.accounts.models import Account


class Transaction(Base):
    amount: Mapped[int]
    signature: Mapped[str]
    account_id: Mapped[int]
    transaction_id: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="transactions")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def to_dict(self):
        return {
            "transation_id": self.transaction_id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "amount": self.amount,
            "signature": self.signature,
        }
