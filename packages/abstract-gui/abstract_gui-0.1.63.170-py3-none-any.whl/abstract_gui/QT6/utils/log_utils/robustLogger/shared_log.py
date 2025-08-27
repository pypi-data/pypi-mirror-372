from __future__ import annotations
import os, sys, logging, threading, traceback, queue
from logging.handlers import RotatingFileHandler
from typing import Optional, Callable, Union
from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QtMsgType, qInstallMessageHandler

# ── paths ────────────────────────────────────────────────────────────────
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
os.makedirs(CACHE_DIR, exist_ok=True)
LOG_FILE = os.path.join(CACHE_DIR, "finder.log")

# ── singletons / guards ─────────────────────────────────────────────────
_LOGGING_WIRED = False
_QT_MSG_HOOKED = False
_SERVICE_SINGLETON: "LogService|None" = None

def get_log_file_path() -> str:
    return LOG_FILE

# ── core logging wiring ─────────────────────────────────────────────────
def setup_root_logging(level=logging.DEBUG, stderr_level=logging.INFO) -> None:
    global _LOGGING_WIRED
    if _LOGGING_WIRED: return
    _LOGGING_WIRED = True

    root = logging.getLogger()
    root.setLevel(level)

    if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == LOG_FILE for h in root.handlers):
        f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        f.setLevel(level)
        f.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"))
        root.addHandler(f)

    if not any(isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stderr for h in root.handlers):
        c = logging.StreamHandler(sys.stderr)
        c.setLevel(stderr_level)
        c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        root.addHandler(c)

def install_python_exception_hooks() -> None:
    def _fmt(e, v, tb): return "".join(traceback.format_exception(e, v, tb))
    def excepthook(exctype, value, tb):
        logging.critical("UNCAUGHT EXCEPTION:\n%s", _fmt(exctype, value, tb))
    sys.excepthook = excepthook

    def threading_excepthook(args):
        logging.critical("THREAD EXCEPTION:\n%s",
                         "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
    threading.excepthook = threading_excepthook  # py>=3.8

def install_qt_message_hook() -> None:
    global _QT_MSG_HOOKED
    if _QT_MSG_HOOKED: return
    _QT_MSG_HOOKED = True

    def qt_message_handler(mode, ctx, message):
        level = {
            QtMsgType.QtDebugMsg: logging.DEBUG,
            QtMsgType.QtInfoMsg: logging.INFO,
            QtMsgType.QtWarningMsg: logging.WARNING,
            QtMsgType.QtCriticalMsg: logging.ERROR,
            QtMsgType.QtFatalMsg: logging.CRITICAL,
        }.get(mode, logging.INFO)
        logging.log(level, "Qt: %s (%s:%s)", message, ctx.file or "unknown", ctx.line or 0)
    qInstallMessageHandler(qt_message_handler)

# ── queue handler + bridge ───────────────────────────────────────────────
class LogQueueHandler(logging.Handler):
    def __init__(self, q: "queue.Queue[str]", *, level=logging.DEBUG, fmt: Optional[logging.Formatter] = None):
        super().__init__(level=level)
        self.q = q
        self.setFormatter(fmt or logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    def emit(self, record: logging.LogRecord) -> None:
        try: self.q.put_nowait(self.format(record))
        except Exception: pass

class QtLogBridge(QtCore.QObject):
    def __init__(self, widget: QtWidgets.QPlainTextEdit, q: "queue.Queue[str]",
                 *, interval_ms=120, batch=500, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.q = q
        self.batch = batch
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self._drain)
        self.timer.start()

    @QtCore.pyqtSlot()
    def _drain(self):
        cursor = self.widget.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.widget.setTextCursor(cursor)
        for _ in range(self.batch):
            try:
                line = self.q.get_nowait()
            except queue.Empty:
                break
            self.widget.appendPlainText(line)

# ── the service you’ll use everywhere ────────────────────────────────────
class LogService:
    """
    One shared queue + handler; attach the same stream to many widgets uniformly.
    """
    def __init__(self):
        setup_root_logging()
        install_python_exception_hooks()
        install_qt_message_hook()

        self.q: "queue.Queue[str]" = queue.Queue()
        self.handler = LogQueueHandler(self.q)
        self._attached_to_root = False
        self._bridges: list[QtLogBridge] = []

        self.attach_to_root()

    def attach_to_root(self):
        if self._attached_to_root: return
        logging.getLogger().addHandler(self.handler)
        self._attached_to_root = True

    def detach_from_root(self):
        if not self._attached_to_root: return
        logging.getLogger().removeHandler(self.handler)
        self._attached_to_root = False

    def _make_view(self, parent: QtWidgets.QWidget) -> QtWidgets.QPlainTextEdit:
        view = QtWidgets.QPlainTextEdit(parent)
        view.setReadOnly(True)
        view.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        view.setObjectName("abstract_log_view")
        return view

    def attach_log(self, host: QtWidgets.QWidget, *, place_in: Optional[QtWidgets.QLayout]=None,
                   with_label=True) -> QtWidgets.QPlainTextEdit:
        """
        Mount a log view inside host (or given layout) and start streaming.
        Returns the QPlainTextEdit so you can style or move it.
        """
        if place_in is None:
            layout = host.layout()
            if layout is None:
                layout = QtWidgets.QVBoxLayout(host)
                host.setLayout(layout)
        else:
            layout = place_in

        if with_label:
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel("Logs"))
            row.addStretch(1)
            layout.addLayout(row)

        view = self._make_view(host)
        layout.addWidget(view)
        self._bridges.append(QtLogBridge(view, self.q, parent=host))
        return view

# singleton accessor
def get_log_service() -> LogService:
    global _SERVICE_SINGLETON
    if _SERVICE_SINGLETON is None:
        _SERVICE_SINGLETON = LogService()
    return _SERVICE_SINGLETON

# optional mini runner
def startConsole(widget_or_cls: Union[type[QtWidgets.QWidget], QtWidgets.QWidget], *args, **kwargs) -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    win = widget_or_cls(*args, **kwargs) if isinstance(widget_or_cls, type) else widget_or_cls
    win.show()
    return app.exec()
