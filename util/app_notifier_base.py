from abc import abstractmethod
from util.app import App
from threading import Event

class AppNotifierBase:
    def __init__(self, app: App) -> None:
        self.app = app
        self.event = Event()
        self.finished = False

    def _check_event(self):
        if self.event.is_set():
            self.event.clear()
            self.notify()
        if not self.finished:
            self.app.add_event(self._check_event)

    def start(self):
        self.app.add_event(self._check_event)

    @abstractmethod
    def notify(self):
        raise NotImplementedError()