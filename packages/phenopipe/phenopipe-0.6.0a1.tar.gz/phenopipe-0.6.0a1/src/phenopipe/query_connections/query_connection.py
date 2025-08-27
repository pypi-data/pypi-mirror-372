from abc import ABC, abstractmethod
from pydantic import BaseModel


class QueryConnection(BaseModel, ABC):
    @abstractmethod
    def get_query_df(self): ...

    @abstractmethod
    def get_cache(self): ...
