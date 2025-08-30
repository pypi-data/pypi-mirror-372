from PySide6.QtWidgets import QProgressBar

class ProgressBar(QProgressBar):
    """A simple progress bar widget."""

    def __init__(self, min_val: int = 0, max_val: int = 100, default_val: int = 0, parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setValue(default_val)
        
    def get_value(self) -> int:
        return self.value()
        
    def set_value(self, value: int):
        self.setValue(value) 