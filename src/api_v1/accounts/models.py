from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.base import Base

if TYPE_CHECKING:
    from src.api_v1.users.models import User


class Account(Base):
    balance: Mapped[int] = mapped_column(default=0)
    user: Mapped["User"] = relationship(back_populates="accounts")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": self.balance,
        }
