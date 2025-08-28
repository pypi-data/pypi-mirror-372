import os
import datetime
import glob
from . import config, html_template


class LogWriter:
    def __init__(self):
        self.filename = os.path.join(config.log_dir, config.main_filename)
        os.makedirs(config.log_dir, exist_ok=True)
        if not os.path.exists(self.filename):
            self._create_log_file()

    def _create_log_file(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(html_template.html_header)

    def _rotate_file(self):
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_filename = os.path.join(
            config.log_dir, f"{ts}_{config.main_filename}")
        os.rename(self.filename, new_filename)
        self._create_log_file()

        # mantém apenas os N arquivos mais recentes
        files = sorted(glob.glob(os.path.join(
            config.log_dir, "*.html")), key=os.path.getctime)
        if len(files) > config.max_files:
            os.remove(files[0])

    def write(self, line: str):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) >= config.max_size:
            self._rotate_file()

        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(line)
