import jsonpickle
from abc import ABC


class Message(ABC):
    def serialize(self):
        return jsonpickle.encode(self)

    @staticmethod
    def deserialize(serialized_message: str):
        return jsonpickle.decode(serialized_message)

    @property
    def message_type(self):
        return self.__class__.__name__
