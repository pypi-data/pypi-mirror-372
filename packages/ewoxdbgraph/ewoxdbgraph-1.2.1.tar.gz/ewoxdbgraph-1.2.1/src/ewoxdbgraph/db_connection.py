from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
from neo4j import AsyncSession
from ewoxdbgraph.interfaces.idb_engine import IDBEngine

class DBConnection():
    def __init__(self, engine:IDBEngine) -> None:
        self._engine:IDBEngine = engine
        self._session:AsyncSession | None = None


    async def __aenter__(self) -> AsyncSession:
        """ Enter & Exit to use together with the WITH statement. """
        self._session = self._engine.get_session()
        if self._session is None:
            raise RuntimeError("Session is not initialized. Call setup() first.")

        return self._session


    async def __aexit__(self, exc_type, exc_value, tb):
        """ Exit the context manager and close the session. """
        if self._session is not None:
            await self._session.close()


    def __enter__(self) -> AsyncSession:
        """ Enter & Exit to use together with the WITH statement. """
        self._session = self._engine.get_session()
        if self._session is None:
            raise RuntimeError("Session is not initialized. Call setup() first.")

        return self._session


    def __exit__(self, exc_type, exc_value, tb):
        """ Exit the context manager and close the session. """
        if self._session is not None:
            self._session.close()
