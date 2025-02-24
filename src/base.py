import pydantic
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
    declared_attr)


class Base(DeclarativeBase,
           # MappedAsDataclass,
           # dataclass_callable=pydantic.dataclasses.dataclass,
           ):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)
