import json
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6.QtCore import QTimer

from RQrive.FileDownloader import FileDownloader
from RQrive.Webview import Webview


class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.setWindowTitle("RQrive")
        self.setStatusBar(QStatusBar())
        self._config = config
        self._transition_timer = QTimer()
        self._transition_timer.timeout.connect(self._start_download_flow)
        if config is None:
            self._start_login_flow()
        else:
            self._start_download_flow()
        self.showMaximized()

    def _start_login_flow(self):
        webview = Webview(self._set_logged_in)
        self.setCentralWidget(webview)
        self.statusBar().showMessage(
            "Logging in. Will automatically close once you successfully log in."
        )

    def _set_logged_in(self, config: dict):
        self._config = config
        config_file = Path('config.json').resolve()
        with config_file.open('w') as file:
            json.dump(config, file)
        self.statusBar().showMessage(f"Logging in as {config['Email']}")
        self._transition_timer.start(1000)

    def _start_download_flow(self):
        self._transition_timer.stop()
        if self._config is not None:
            self.statusBar().showMessage(f"Logged in as {self._config['Email']}")
            login_view = FileDownloader(self._config)
            self.setCentralWidget(login_view)
