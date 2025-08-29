from .base.BaseFactory import StringDecoratorFactory
from ..decorator.CaseDecorator import CaseDecorator

class CaseDecoratorFactory(StringDecoratorFactory):
    def create_decorator(self):
        return CaseDecorator()