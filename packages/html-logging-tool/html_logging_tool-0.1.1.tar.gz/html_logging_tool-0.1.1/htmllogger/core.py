import threading
import queue
import datetime
import time
import traceback
import atexit
from .writer import LogWriter


class Logger:
    def __init__(self):
        self.queue = queue.Queue()
        self.writer = LogWriter()
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        atexit.register(self.flush)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                line = self.queue.get(timeout=0.1)
                self.writer.write(self._handle_msg_format(line))
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in logger worker: {e}")

    def _handle_msg_format(self, msg):
        return f"{str(msg)}\n"

    def log(self, message, color="white"):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f'<br><font color="{color}">{ts} - {message}</font>'
        self.queue.put(line)

    def error(self, message):
        self.log(f"** {message}", color="red")

    def report_exception(self, exc, timeout=None):
        err = traceback.format_exc()
        self.log(f"**** Exception: <code>{err}</code>", color="red")
        if timeout:
            time.sleep(timeout)

    def flush(self):
        """Processa todas as mensagens pendentes antes do término"""
        self._stop_event.set()

        # Processa mensagens remanescentes manualmente
        while not self.queue.empty():
            try:
                line = self.queue.get_nowait()
                self.writer.write(self._handle_msg_format(line))
                self.queue.task_done()
            except queue.Empty:
                break

        # Aguarda a thread terminar
        self.thread.join(timeout=0.1)
