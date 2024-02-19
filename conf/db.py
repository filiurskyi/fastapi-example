import contextlib
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from conf.secret import DB_URI


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a context manager that allows you to use the database session in an async way.
            It will automatically rollback and close the session if there is an exception, or commit and close it otherwise.
            Example:

        :param self: Represent the instance of the class
        :return: A context manager, which is used in the following way:
        :doc-author: Trelent
        """
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as e:
            logging.error("Failed to connect to database. Error: ", e)
            await session.rollback()
        finally:
            await session.close()


session_manager = DatabaseSessionManager(DB_URI)


async def get_db():
    """
    The get_db function is a context manager that returns an asyncpg connection
    to the database. It uses the session_manager to create a new session, and then
    yields it. The yield statement allows us to use this function as an asynchronous
    context manager, which means we can use it with Python's async with statement.

    :return: A generator object
    :doc-author: Trelent
    """
    async with session_manager.session() as session:
        yield session
