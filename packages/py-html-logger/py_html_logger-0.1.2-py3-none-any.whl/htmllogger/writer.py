# writer.py
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
            config.log_dir, "*.html")), key=os.path.getctime, reverse=True)
        if len(files) > config.max_files:
            for old_file in files[config.max_files:]:
                os.remove(old_file)

    def write(self, line: str):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) >= config.max_size:
            self._rotate_file()

        # Lê o conteúdo atual do arquivo
        with open(self.filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Substitui o marcador pelo conteúdo novo + marcador
        new_content = content.replace("<!-- LOG_CONTENT -->", "\n" + line + "<!-- LOG_CONTENT -->")

        # Escreve o conteúdo atualizado de volta no arquivo
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(new_content)
