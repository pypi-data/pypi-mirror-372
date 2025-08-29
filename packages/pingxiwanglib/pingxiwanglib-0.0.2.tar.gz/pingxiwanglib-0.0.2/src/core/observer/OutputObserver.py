from abc import ABC, abstractmethod

class OutputObserver(ABC):
    @abstractmethod
    def update(self, text):
        pass