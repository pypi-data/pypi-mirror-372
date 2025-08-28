# basicbrowser.py
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLineEdit, QPushButton, QToolBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction
import sys

class YappatronSettings:
    def __init__(
        self,
        start_url="https://google.com",
        width=1200,
        height=800,
        show_toolbar=True,
        show_new_tab_button=True,
        show_back_forward=True,
        show_refresh=True,
        search_engine="https://www.google.com/search?q="
    ):
        self.start_url = start_url
        self.width = width
        self.height = height
        self.show_toolbar = show_toolbar
        self.show_new_tab_button = show_new_tab_button
        self.show_back_forward = show_back_forward
        self.show_refresh = show_refresh
        self.search_engine = search_engine


class _Browser(QMainWindow):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or YappatronSettings()

        self.setWindowTitle("Yappatron Browser")
        self.setGeometry(100, 100, self.settings.width, self.settings.height)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar
        if self.settings.show_toolbar:
            nav_bar = QToolBar("Navigation")
            self.addToolBar(nav_bar)

            # Back / Forward / Refresh buttons
            if self.settings.show_back_forward:
                back_btn = QAction("Back", self)
                back_btn.triggered.connect(self.go_back)
                nav_bar.addAction(back_btn)

                forward_btn = QAction("Forward", self)
                forward_btn.triggered.connect(self.go_forward)
                nav_bar.addAction(forward_btn)

            if self.settings.show_refresh:
                reload_btn = QAction("Refresh", self)
                reload_btn.triggered.connect(self.reload)
                nav_bar.addAction(reload_btn)

            # URL entry + Go button
            self.url_entry = QLineEdit()
            self.url_entry.returnPressed.connect(self.load_url)
            nav_bar.addWidget(self.url_entry)

            go_btn = QPushButton("Go")
            go_btn.clicked.connect(self.load_url)
            nav_bar.addWidget(go_btn)

            # New tab button
            if self.settings.show_new_tab_button:
                new_tab_btn = QPushButton("+")
                new_tab_btn.clicked.connect(lambda: self.add_tab(self.settings.start_url))
                nav_bar.addWidget(new_tab_btn)
        else:
            self.url_entry = None  # safe fallback

        # Start with one tab
        self.add_tab(self.settings.start_url)

    def add_tab(self, url):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        webview = QWebEngineView()
        webview.setUrl(QUrl(url))
        webview.urlChanged.connect(lambda qurl, tab=tab: self.update_url(qurl, tab))
        webview.titleChanged.connect(lambda title, tab=tab: self.update_tab_title(title, tab))
        layout.addWidget(webview)

        self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentWidget(tab)

        tab.webview = webview

    def load_url(self):
        if self.url_entry is None:
            return
        url = self.url_entry.text()
        if not url.startswith("http"):
            url = self.settings.search_engine + url.replace(" ", "+")
        current_tab = self.tabs.currentWidget()
        current_tab.webview.setUrl(QUrl(url))

    def go_back(self):
        self.tabs.currentWidget().webview.back()

    def go_forward(self):
        self.tabs.currentWidget().webview.forward()

    def reload(self):
        self.tabs.currentWidget().webview.reload()

    def update_url(self, qurl, tab):
        if self.url_entry and tab == self.tabs.currentWidget():
            self.url_entry.setText(qurl.toString())

    def update_tab_title(self, title, tab):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, title)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)


def run(settings=None):
    """Entry point for users. Optional settings object."""
    app = QApplication(sys.argv)
    browser = _Browser(settings=settings)
    browser.show()
    sys.exit(app.exec())
