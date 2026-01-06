from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from RQrive.api import auth


class Webview(QWebEngineView):
    def __init__(self, login_callback):
        super().__init__()
        self._login_callback = login_callback
        cookie_store = self.page().profile().cookieStore()
        self.setUrl(QUrl("https://accounts.google.com/EmbeddedSetup"))
        cookie_store.cookieAdded.connect(self.on_cookie_added)

    def on_cookie_added(self, cookie):
        name = cookie.name().data().decode("utf-8")
        if name == "oauth_token":
            auth_response = auth(cookie.value().data().decode("utf-8"))
            config = {"Email": auth_response["Email"], "Token": auth_response["Token"]}
            self._login_callback(config)
