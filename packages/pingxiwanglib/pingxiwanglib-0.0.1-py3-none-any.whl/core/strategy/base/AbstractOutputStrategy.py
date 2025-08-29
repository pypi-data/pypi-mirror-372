from abc import ABC, abstractmethod

class OutputStrategy(ABC):
    @abstractmethod
    def execute(self, text):
        pass