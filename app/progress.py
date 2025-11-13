"""
Shared progress tracking module for the application.
This module provides a process-wide progress emitter that converter code can call
from worker threads. The emitter uses Qt signals so GUI updates happen on the
main thread.
"""

from PySide6.QtCore import QObject, Signal

# Internal counters for progress values (0-100)
_progress_value_1 = 0
_progress_value_2 = 0


class _Emitter(QObject):
    progress1_changed = Signal(int)
    progress2_changed = Signal(int)


# singleton emitter
_emitter = _Emitter()


def set_progress_window(window):
    """Connect the emitter signals to the given MainWindow instance.

    The converter code should call update_progress/update_progress_2 which
    will emit signals; the main window will receive them and update widgets
    on the GUI thread.
    """
    # connect signals to window slots (safe across multiple calls)
    try:
        _emitter.progress1_changed.disconnect()
    except Exception:
        pass
    try:
        _emitter.progress2_changed.disconnect()
    except Exception:
        pass

    _emitter.progress1_changed.connect(window.set_progress)
    _emitter.progress2_changed.connect(window.set_progress_2)


def update_progress(increment):
    """Increment first progress counter and emit new value (0-100)."""
    global _progress_value_1
    _progress_value_1 = min(100, max(0, _progress_value_1 + int(increment)))
    _emitter.progress1_changed.emit(int(_progress_value_1))


def update_progress_2(increment):
    """Increment second progress counter and emit new value (0-100)."""
    global _progress_value_2
    _progress_value_2 = min(100, max(0, _progress_value_2 + int(increment)))
    _emitter.progress2_changed.emit(int(_progress_value_2))


def set_progress(value):
    """Set first progress to absolute value and emit signal."""
    global _progress_value_1
    _progress_value_1 = int(max(0, min(100, value)))
    _emitter.progress1_changed.emit(_progress_value_1)


def set_progress_2(value):
    """Set second progress to absolute value and emit signal."""
    global _progress_value_2
    _progress_value_2 = int(max(0, min(100, value)))
    _emitter.progress2_changed.emit(_progress_value_2)
