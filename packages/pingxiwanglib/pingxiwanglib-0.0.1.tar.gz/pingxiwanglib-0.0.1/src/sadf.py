
from src.core.manager.OutputManager import OutputManager
from src.core.enums.OutputType import OutputType

if __name__ == "__main__":
    manager = OutputManager(output_color=True)
    manager.process("Hello world", OutputType.Console)
