# --- make any top-level widget "user-expandable" ----------------------------
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QSizePolicy, QTextEdit
from PyQt6.QtCore import Qt, QSize

def ensure_user_resizable(win: QWidget, *, initial_size: tuple[int,int]=(900, 700), min_size: tuple[int,int]=(400, 300)):
    """
    Ensures a top-level window can be resized by the user and its content expands.
    Call right after you construct the window, before .show().
    """
    # 1) make sure it's a top-level window with normal window flags
    win.setWindowFlag(Qt.Window, True)

    # 2) give it a reasonable starting & minimum size (but NOT fixed)
    w0, h0   = initial_size
    wmin, hmin = min_size
    try:
        win.setMinimumSize(QSize(wmin, hmin))
        win.resize(w0, h0)
    except Exception:
        pass  # if some container refuses, it's fine

    # 3) ensure there is a layout and that children can expand
    def _ensure_expanding(widget: QWidget):
        sp = widget.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        widget.setSizePolicy(sp)

    if isinstance(win, QMainWindow):
        central = win.centralWidget()
        if central is None:
            # create a simple expanding central area if none exists
            central = QWidget(win)
            layout = QVBoxLayout(central)
            layout.setContentsMargins(8, 8, 8, 8)
            # if you already have a log view on the instance, add it so it stretches
            te = getattr(win, "log", None)
            if isinstance(te, QTextEdit):
                _ensure_expanding(te)
                layout.addWidget(te)
            else:
                # placeholder so the window shows something and expands
                placeholder = QTextEdit()
                placeholder.setReadOnly(True)
                placeholder.setPlaceholderText("Logs will appear here…")
                _ensure_expanding(placeholder)
                layout.addWidget(placeholder)
            win.setCentralWidget(central)
        _ensure_expanding(central)
    else:
        # plain QWidget: make sure it has a layout that can stretch
        if win.layout() is None:
            lay = QVBoxLayout(win)
            lay.setContentsMargins(8, 8, 8, 8)
            te = getattr(win, "log", None)
            if isinstance(te, QTextEdit):
                _ensure_expanding(te)
                lay.addWidget(te)

        _ensure_expanding(win)

    # 4) if you use splitters, tell them which pane should stretch
    try:
        for child in win.findChildren(QWidget):
            _ensure_expanding(child)
    except Exception:
        pass
