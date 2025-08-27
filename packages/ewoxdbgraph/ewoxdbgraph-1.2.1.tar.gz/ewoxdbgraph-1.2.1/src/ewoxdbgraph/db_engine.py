from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
from datetime import date, datetime, timedelta
import asyncio
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, AuthError
from ewoxdbgraph.db_settings import DBSettings
from ewoxdbgraph.interfaces.idb_engine import IDBEngine


class DBEngine(IDBEngine):
    def __init__(self, settings:DBSettings) -> None:
        self._driver:AsyncDriver = None
        self._settings:DBSettings = settings


    async def setup(self)-> None:
        """ Setup the driver connection.
        This method initializes the driver connection to the Neo4j database.
        It uses retry logic to handle connection failures. """
        self._driver = await self._connect()


    async def dispose(self) -> None:
        """ Dispose of the driver connection. """
        if self._driver is not None:
            await self._driver.close()


    async def _connect(self) -> AsyncDriver:
        """ Connect to the Neo4j database with retry logic.
        Args:
        Returns:
            AsyncDriver: An instance of AsyncGraphDatabase driver.
        Raises:
            ServiceUnavailable: If the database is unavailable after all retries.
            AuthError: If authentication fails after all retries.
        """
        auth:Tuple[str,str] = (self._settings.user, self._settings.password)
        driver:AsyncDriver = AsyncGraphDatabase.driver(self._settings.url, auth=auth)

        for attempt in range(1, self._settings.num_retries + 1):
            try:
                await driver.verify_connectivity()
                print("Connected to database")
                return driver
            except (ServiceUnavailable, AuthError) as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == self._settings.num_retries:
                    raise

                sleep:float = self._settings.backoff_seconds ** attempt
                print(f"Retrying in {sleep}s...")

                await asyncio.sleep(sleep)


    def get_session(self) -> AsyncSession:
        """ Get a session from the driver.
        Returns:
            AsyncGraphDatabase.AsyncSession: An instance of AsyncSession.
        """
        if self._driver is None:
            raise RuntimeError("Driver is not initialized. Call setup() first.")
        
        return self._driver.session()
