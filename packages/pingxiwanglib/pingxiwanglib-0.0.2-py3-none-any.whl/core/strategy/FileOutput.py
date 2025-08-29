from abc import ABC, abstractmethod
from datetime import datetime
from .base.AbstractOutputStrategy import OutputStrategy

class FileOutput(OutputStrategy):
    def execute(self, text):
        with open('output.txt', 'a') as f:
            f.write(f"[FILE] {datetime.now()}: {text}\n")