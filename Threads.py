import threading
import queue
from siler_audio import Silero


class SpeakThread:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = False
        self.worker = None
        self.stop_flag = object()
        self.cancel_flag = object()
        self.current_speaking = False
        self.audio_silero = Silero()

    def start(self):

        if self.running:
            return
        self.running = True
        self.worker = threading.Thread(target=self.process_queue, daemon=True)
        self.worker.start()
        print('Очередь запущена')

    def add(self, func, *args):
        if not self.running:
            raise RuntimeError('Очередь не запущена')
        task = (func, args)
        self.queue.put(task)

    def process_queue(self):

        while self.running:
            try:
                task = self.queue.get(timeout=0.5)
                if task is self.stop_flag:
                    self.queue.task_done()
                    break

                func, args = task

                func(*args)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f'Error {e}')

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.clear()

    def clear(self):
        self.queue.queue.clear()
