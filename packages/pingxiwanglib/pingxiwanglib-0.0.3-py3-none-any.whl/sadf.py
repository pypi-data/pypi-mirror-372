
from src.pingxiwanglib.manager.OutputManager import OutputManager
from src.pingxiwanglib.enums.OutputType import OutputType

if __name__ == "__main__":
    manager = OutputManager(output_color=True)
    manager.process("Hello world", OutputType.Console)
