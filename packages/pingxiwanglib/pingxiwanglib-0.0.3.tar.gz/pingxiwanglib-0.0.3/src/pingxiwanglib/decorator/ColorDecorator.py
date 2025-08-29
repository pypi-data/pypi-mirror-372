import random
from .StringDecorator import StringDecorator

class ColorDecorator(StringDecorator):
    COLORS = {'red': '\033[91m', 'green': '\033[92m', 'end': '\033[0m'}

    def decorate(self, text):
        color = random.choice(list(self.COLORS.keys())[:-1])
        return f"{self.COLORS[color]}{text}{self.COLORS['end']}"