from abc import ABC, abstractmethod


class Consumer(ABC):
    @abstractmethod
    def consume(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def __enter__(self):
        self.consume()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
