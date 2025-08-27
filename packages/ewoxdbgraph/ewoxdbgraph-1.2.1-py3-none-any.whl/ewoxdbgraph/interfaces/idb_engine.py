from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from abc import ABC, abstractmethod
from neo4j import AsyncSession

T = TypeVar('T')


class IDBEngine(ABC):
    @abstractmethod
    async def setup(self)-> None:
        """ Set up the database engine. """
        raise NotImplementedError("Implement inhereted method")
    
    @abstractmethod
    async def dispose(self) -> None:
        """ Dispose of the database engine. """
        raise NotImplementedError("Implement inhereted method")
    
    @abstractmethod
    def get_session(self) -> AsyncSession:
        """ Get a session for database operations. """
        raise NotImplementedError("Implement inhereted method")
