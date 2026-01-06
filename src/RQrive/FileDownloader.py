from PySide6.QtCore import QSize, Qt, QTimer

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QWidget,
)

import RQrive.api as api
from hurry.filesize import size as readable_size


class FileDownloader(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self._token = api.access_token(config)
        self._file_name = None
        self._file_size = 0
        self._file_id = None
        self._download_object = None

        self._form_layout = QFormLayout(self)

        self._url_field = QLineEdit(self)
        self._url_field.textChanged.connect(self._on_url_field_updated)
        self._form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self._url_field)

        self._url_field_label = QLabel("File URL/ ID", self)
        self._form_layout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self._url_field_label
        )

        self._info_label = QLabel(self)
        self._info_label.setMinimumSize(QSize(0, 100))
        self._form_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self._info_label)

        self._action_button = QPushButton(self)
        self._action_button.pressed.connect(self._on_action_button_pressed)
        self._form_layout.setWidget(
            4, QFormLayout.ItemRole.SpanningRole, self._action_button
        )

        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.pressed.connect(self._on_cancel_button_pressed)
        self._form_layout.setWidget(
            5, QFormLayout.ItemRole.SpanningRole, self._cancel_button
        )

        self._progress_bar = QProgressBar(self)
        self._progress_bar_timer = QTimer()
        self._progress_bar_timer.timeout.connect(self._on_progress_updated)
        self._form_layout.setWidget(
            3, QFormLayout.ItemRole.SpanningRole, self._progress_bar
        )

        self._title = QLabel(self)
        self._title.setMinimumSize(QSize(100, 100))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._form_layout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self._title)

        self._show_prompt_menu()

    def _on_progress_updated(self):
        if self._download_object is not None:
            percentage = (self._download_object.progress * 100) // self._file_size
            self._progress_bar.setValue(percentage)
            if percentage == 100:
                self._action_button.setText("Ok")
                self._action_button.setEnabled(True)
                self._progress_bar_timer.stop()

    def _on_url_field_updated(self):
        text = self._url_field.text()
        if "/" in text:
            try:
                id_index = text.index("/d/")
                text = text[id_index + 3 :]
                if text.find("/") != -1:
                    text = text[: text.find("/")]
                elif text.find("?") != -1:
                    text = text[: text.find("?")]
            except ValueError:
                self._action_button.setEnabled(False)
        if len(text) != 0 and text != self._file_id:
            self._action_button.setEnabled(True)
            self._file_id = text
        else:
            self._action_button.setEnabled(False)

    def _on_action_button_pressed(self):
        if self._file_id is None:
            return
        if self._file_name is None:
            metadata = api.get_file_info(self._token, self._file_id)
            self._info_label.setText(
                f"File name: {metadata['title']}\nFile Size: {readable_size(int(metadata['fileSize']))}"
            )
            self._file_size = int(metadata["fileSize"])
            self._file_name = metadata["title"]
            self._show_download_menu()
        elif self._download_object is None:
            self._download_object = api.File(
                self._token, self._file_id, self._file_name
            )
            self._download_object.download()
            self._action_button.setEnabled(False)
            self._progress_bar_timer.start(500)
            self._progress_bar.setVisible(True)
        else:
            self._show_prompt_menu()

    def _on_cancel_button_pressed(self):
        if self._file_id is None or self._file_name is None:
            return
        if self._download_object is not None:
            self._download_object.cancel()
            self._action_button.setEnabled(True)
        else:
            self._show_prompt_menu()

    def _show_prompt_menu(self):
        self._file_name = None
        self._title.setText("Download a file from Google Drive")
        self._action_button.setText("Get file information")
        self._action_button.setEnabled(self._file_id is not None)
        self._url_field.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._info_label.setVisible(False)
        self._cancel_button.setVisible(False)

    def _show_download_menu(self):
        self._title.setText(f"Download {self._file_name}")
        self._action_button.setText("Download file")
        self._action_button.setEnabled(True)
        self._url_field.setEnabled(False)
        self._progress_bar.setVisible(False)
        self._info_label.setVisible(True)
        self._cancel_button.setVisible(True)
