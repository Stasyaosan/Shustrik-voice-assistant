import threading
import queue


class SpeakThread:

    def __init__(self):
        self.queue = queue.Queue
        self.running = False
        self.worker = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.worker = threading.Thread(target=self.process_queue, daemon=True)

    def process_queue(self):
        pass

    def add(self):
        pass

    def stop(self):
        pass
