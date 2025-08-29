from .OutputObserver import OutputObserver
class LoggerObserver(OutputObserver):
    def update(self, text):
        print(f"[LOG] Output observed: {text}")