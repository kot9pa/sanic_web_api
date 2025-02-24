from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from src.config import settings


class Database:
    def __init__(self, echo: bool = None):
        self.engine = create_async_engine(
            url=settings.get_db_url(),
            echo=settings.DB_ECHO if None else echo,
        )
        self._session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def create_session(self) -> AsyncSession:
        return self._session_factory()
