from abc import ABC, abstractmethod

class StringDecoratorFactory(ABC):
    """
    decorate string
    """
    @abstractmethod
    def create_decorator(self):
        pass