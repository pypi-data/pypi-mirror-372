from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

class CollapsibleLogPanel(QWidget):
    """
    A simple panel that shows a header row with a static toggle button and a content widget below.
    The content widget can be any QWidget (we'll use a QSplitter containing log panes).
    """
    def __init__(self, title: str, content_widget: QWidget, parent=None):
        super().__init__(parent)
        self._content = content_widget
        self._content.setParent(self)

        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(22, 22)
        self.toggle_btn.setToolTip("Show / hide logs (Ctrl+L)")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)
        header.addWidget(self.toggle_btn)
        header.addWidget(self.title_label)
        header.addStretch(1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(header)
        # Wrap content in a frame so we can hide/show it cleanly
        frame = QFrame(self)
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self._content)
        root.addWidget(frame)

        self._frame = frame
        self.toggle_btn.toggled.connect(self._on_toggle)
        # keyboard shortcut
        self.toggle_btn.setShortcut("Ctrl+L")

    def _on_toggle(self, checked: bool):
        # flip arrow glyph
        self.toggle_btn.setText("▲" if not checked else "▼")
        # hide or show the frame containing the content
        self._frame.setVisible(checked)

    def expand(self):
        self.toggle_btn.setChecked(True)

    def collapse(self):
        self.toggle_btn.setChecked(False)

    def is_expanded(self) -> bool:
        return self.toggle_btn.isChecked()
