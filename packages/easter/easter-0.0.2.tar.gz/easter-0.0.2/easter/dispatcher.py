from abc import ABC, abstractmethod
from easter.message import Message


class Dispatcher(ABC):
    @abstractmethod
    def dispatch(self, message: Message):
        pass
