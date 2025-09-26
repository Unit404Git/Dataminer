# main_qt.py
import sys
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox
)
from processor import process_directory


class Worker(QObject):
    progress = Signal(int, int, str)   # current, total, message
    finished = Signal()
    error = Signal(str)

    @Slot(str)
    def run(self, directory: str):
        try:
            total, iterator = process_directory(directory)
            if total <= 0:
                self.progress.emit(0, 1, "Nothing to do")
                self.finished.emit()
                return

            current = 0
            for message in iterator:
                current += 1
                self.progress.emit(current, total, message)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Your App")
        self.selected_dir = None
        self.thread = None
        self.worker = None

        layout = QVBoxLayout(self)

        # Directory row
        dir_row = QHBoxLayout()
        self.pick_btn = QPushButton("Pick Directory")
        self.pick_btn.clicked.connect(self.pick_directory)
        self.dir_label = QLabel("No directory selected.")
        dir_row.addWidget(self.pick_btn)
        dir_row.addWidget(self.dir_label)
        layout.addLayout(dir_row)

        # Progress
        self.progress_label = QLabel("Waiting to start...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        # Action buttons
        action_row = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_processing)
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.exit_btn)
        layout.addLayout(action_row)

        self.resize(600, 160)

    def pick_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select directory")
        if directory:
            self.selected_dir = directory
            self.dir_label.setText(f"Selected: {directory}")

    def start_processing(self):
        if not self.selected_dir:
            QMessageBox.warning(self, "Missing directory",
                                "Please select a directory first.")
            return

        # Reset UI
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.start_btn.setEnabled(False)
        self.pick_btn.setEnabled(False)

        # Threaded worker so UI stays responsive
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(lambda: self.worker.run(self.selected_dir))
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        # Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_progress(self, current: int, total: int, message: str):
        percent = int(current / total * 100) if total else 0
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"{message} ({current}/{total})")

    def on_finished(self):
        self.progress_label.setText("Done ✅")
        self.start_btn.setEnabled(True)
        self.pick_btn.setEnabled(True)

    def on_error(self, msg: str):
        QMessageBox.critical(self, "Error", msg)
        self.progress_label.setText("Error")
        self.start_btn.setEnabled(True)
        self.pick_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
