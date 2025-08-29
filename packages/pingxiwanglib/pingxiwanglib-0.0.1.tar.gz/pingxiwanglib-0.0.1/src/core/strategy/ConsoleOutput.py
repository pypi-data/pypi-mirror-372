from .base.AbstractOutputStrategy import OutputStrategy

class ConsoleOutput(OutputStrategy):
    def execute(self, text):
        print(f"[CONSOLE] {text}")