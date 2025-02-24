from typing import TYPE_CHECKING
from sqlalchemy import text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.base import Base
from .schemas import Role

if TYPE_CHECKING:
    from src.api_v1.accounts.models import Account
    from src.api_v1.transactions.models import Transaction


class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    fullname: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[Role] = mapped_column(
        default=Role.user, server_default=text("'user'"))

    accounts: Mapped[list["Account"]] = relationship(back_populates="user",
                                                     cascade="all, delete")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user",
                                                             cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
        }
