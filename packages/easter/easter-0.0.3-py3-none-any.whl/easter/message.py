import jsonpickle
from abc import ABC


class Message(ABC):
    def serialize(self):
        return jsonpickle.encode(self)

    @staticmethod
    def deserialize(serialized_message: str):
        try:
            return jsonpickle.decode(serialized_message, on_missing="error")
        except:
            return None

    @property
    def message_type(self):
        return self.__class__.__name__
