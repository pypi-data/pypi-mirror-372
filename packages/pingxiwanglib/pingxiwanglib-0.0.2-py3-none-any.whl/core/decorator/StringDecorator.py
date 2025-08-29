from abc import ABC, abstractmethod

class StringDecorator(ABC):
    @abstractmethod
    def decorate(self, text):
        pass
