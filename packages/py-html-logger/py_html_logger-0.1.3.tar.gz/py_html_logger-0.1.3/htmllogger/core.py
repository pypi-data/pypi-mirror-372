# core.py
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
        self.used_tags = set()  # Armazena todas as tags usadas
        atexit.register(self.flush)

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                line = self.queue.get(timeout=0.1)
                # REMOVA esta linha: formatted_line = self.__handle_msg(line)
                # EM VEZ DISSO, use a linha diretamente:
                self.writer.write(line)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in logger worker: {e}")
                import traceback
                traceback.print_exc()

    def __handle_msg(self, message, color="white", tag=None):
        tag_attr = ""
        if tag:
            if isinstance(tag, str):
                tag = [tag]
            # Adiciona tags ao conjunto de tags usadas
            for t in tag:
                self.used_tags.add(t)
            tag_attr = f" data-tags='{','.join(tag)}'"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f'<br><font color="{color}"{tag_attr}>{ts} - {message}</font>'
        self.queue.put(line)

    def log(self, message, color, tag):
        self.__handle_msg(message, color, tag)

    def info(self, message, color, tag):
        tag_attr = ""
        if tag:
            if isinstance(tag, str):
                tag = [tag]
            # Adiciona tags ao conjunto de tags usadas
            for t in tag:
                self.used_tags.add(t)
            tag_attr = f" data-tags='{','.join(tag)}'"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f'<br><br><font color="{color}"{tag_attr}>{ts} - {message}</font><br>'
        self.queue.put(line)

    def debug(self, message, color, tag):
        self.__handle_msg(f"## DEBUG: {message}", color, tag)

    def warning(self, message, color, tag):
        self.__handle_msg(f"⚠️ {message}", color, tag)

    def error(self, message):
        self.__handle_msg(f"** {message}", color="red", tag="error")

    def report_exception(self, exc, timeout=None):
        err = traceback.format_exc()
        self.__handle_msg(f"**** Exception: <code>{err}</code>", color="red", tag="exception")
        if timeout:
            time.sleep(timeout)

    def flush(self):
        """Processa todas as mensagens pendentes antes do término"""
        self._stop_event.set()

        # Processa mensagens remanescentes manualmente
        processed_count = 0
        while not self.queue.empty() and processed_count < 1000:
            try:
                line = self.queue.get_nowait()
                # REMOVA esta linha: formatted_line = self.__handle_msg(line)
                # EM VEZ DISSO, use a linha diretamente:
                self.writer.write(line)
                self.queue.task_done()
                processed_count += 1
            except queue.Empty:
                break

        # Aguarda a thread terminar
        self.thread.join(timeout=0.2)

    def get_used_tags(self):
        """Retorna todas as tags usadas até o momento"""
        return sorted(list(self.used_tags))
