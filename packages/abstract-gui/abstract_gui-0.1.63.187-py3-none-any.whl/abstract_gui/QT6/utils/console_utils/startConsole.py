from .worker_scans import *
from .collapsable_log_panel import *
from .log_manager import *
from .ensure_resizable import *
# ─────────────────────────── instance augmentation helpers ───────────────────────
def _graceful_shutdown(self):
    for w in list(getattr(self, "_active_workers", [])):
        w.cancel()
    for t in list(getattr(self, "_threads", [])):
        if t.isRunning():
            t.requestInterruption()
            t.quit()
            t.wait(5000)
    self._active_workers = []
    self._threads = []

# ─────────────────────────── runner ───────────────────────────────────────────────
def startConsole(console_class, *args, **kwargs):
    app = QApplication.instance() or QApplication(sys.argv)
    win = console_class(*args, **kwargs)
    get_WorkerScans(win)  # creates win.log (QTextEdit) and other plumbing
    # Ensure main layout
    lay = win.layout() or QtWidgets.QVBoxLayout(win)
    if win.layout() is None:
        win.setLayout(lay)
    # Label + main log (the one created by get_WorkerScans)
    header_row = QHBoxLayout()
    header_row.addWidget(QLabel("Log Output (global):"))
    header_row.addStretch(1)
    lay.addLayout(header_row)
    # Use a horizontal splitter to hold multiple log panes
    splitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal, win)
    # existing log widget created by get_WorkerScans
    splitter.addWidget(win.log)   # win.log is the QTextEdit created earlier
    # wrap the splitter in the collapsible panel
    log_panel = CollapsibleLogPanel("Logs", splitter, parent=win)
    # add to layout (instead of lay.addWidget(splitter))
    lay.addWidget(log_panel)
    attach_textedit_to_logs(win.log, tail_file=None, logger_filter=None)
    # rest of setup...
    ensure_user_resizable(win, initial_size=(1100, 800), min_size=(600, 400))
    keep_capped_across_screen_changes(win, margin=8, fraction=0.95)
    app.aboutToQuit.connect(win._graceful_shutdown)
    win.show()
    return app.exec()


