from ..factory.base.BaseFactory import StringDecoratorFactory
from ..decorator.ColorDecorator import ColorDecorator

class ColorDecoratorFactory(StringDecoratorFactory):
    def create_decorator(self):
        return ColorDecorator()
