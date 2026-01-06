from pathlib import Path
import json

from PySide6.QtWidgets import QApplication
from RQrive.MainWindow import MainWindow

def main():
    app = QApplication()
    config_file = Path('config.json').resolve()
    config = None
    try:
        with config_file.open('r') as file:
            config = json.load(file)
    except json.JSONDecodeError, FileNotFoundError, IOError:
        config = None
    main_window = MainWindow(config)
    app.exec()