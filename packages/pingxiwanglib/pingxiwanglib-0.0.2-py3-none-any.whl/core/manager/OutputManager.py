from ..factory.ColorDecoratorFactory import ColorDecoratorFactory
from ..factory.CaseDecoratorFactory import CaseDecoratorFactory
from ..enums.OutputType import OutputType
from ..strategy.ConsoleOutput import ConsoleOutput
from ..strategy.FileOutput import FileOutput
from ..observer.OutputSubject import OutputSubject
from ..observer.LogObserver import LoggerObserver


class OutputManager:

    def __init__(self, output_color=False):
        self.output_color = output_color
        self._setup()

    def _setup(self):
        factory = ColorDecoratorFactory if self.output_color else CaseDecoratorFactory
        self.decorator_factories = [
            factory
        ]
        self.strategies = {
            OutputType.Console: ConsoleOutput(),
            OutputType.File: FileOutput()
        }
        self.subject = OutputSubject()
        self.subject.attach(LoggerObserver())

    def process(self, text, strategy_type=OutputType.Console):
        for factory in self.decorator_factories:
            decorator = factory.create_decorator(self)
            text = decorator.decorate(text)

            strategy = self.strategies.get(strategy_type, ConsoleOutput())
            strategy.execute(text)

            self.subject.notify(text)