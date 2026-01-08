from abc import ABC, abstractmethod
class MessageQueue(ABC):
    @abstractmethod
    def publish(self, message):
        raise NotImplementedError
    @abstractmethod
    def consume(self, callback):
        raise NotImplementedError
    
