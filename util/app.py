from queue import Queue
import time
from typing import Callable

class App:
    """
    メインループを持つクラス

    メインループで実行する処理は、add_event()で登録する
    """
    def __init__(self):
        self._event_queue = Queue()
        self._finished = False

    def stop(self):
        """
        メインループを終了する
        """
        self._finished = True

    def add_event(self, event: Callable[[], None]):
        self._event_queue.put(event)

    def run(self):
        while not self._finished:
            if self._event_queue.empty():
                time.sleep(0.03)
                continue
            event = self._event_queue.get()
            event()
