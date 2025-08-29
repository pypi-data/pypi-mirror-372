from typing import Any
from abc import ABCMeta
from abc import abstractmethod


class BaseDataSource(metaclass=ABCMeta):
    @property
    def filename(self) -> str:
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def data(self) -> list[dict[str, Any]]:
        raise NotImplementedError("This method should be implemented in subclasses.")

    @abstractmethod
    def load(self):
        raise NotImplementedError("This method should be implemented in subclasses.")
