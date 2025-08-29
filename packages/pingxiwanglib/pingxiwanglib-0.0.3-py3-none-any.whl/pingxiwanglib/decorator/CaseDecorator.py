from .StringDecorator import StringDecorator

class CaseDecorator(StringDecorator):
    def decorate(self, text):
        return ''.join(
            c.upper() if i % 2 == 0 or i % 3 == 0 else c.lower()
            for i, c in enumerate(text)
        )