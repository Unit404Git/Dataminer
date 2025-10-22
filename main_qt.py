import sys
from PySide6.QtCore import QObject, Signal, Slot, QThread, QEvent, QPoint, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox,
    QToolButton, QMenu, QDialog, QTextEdit
)
from processor import process_directory

import resources_rc  # Import the compiled resources


class Worker(QObject):
    progress = Signal(int, int, str)
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


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        help_label = QLabel(
            "This is a help window. Provide useful information here.")
        layout.addWidget(help_label)
        self.setLayout(layout)
        self.apply_styles()

    def apply_styles(self):
        # add others as needed
        files = ["styles/main.qss", "styles/testbutton.qss"]
        css = ""
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as h:
                    css += h.read() + "\n"
            except FileNotFoundError:
                print(f"⚠️ Stylesheet not found: {f}")
        self.setStyleSheet(css)


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log / Console Output")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        close_btn = QPushButton("Schließen", self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def append_text(self, text: str):
        self.text_edit.append(text)


class EmittingStream(QObject):
    textWritten = Signal(str)

    def write(self, text):
        if text.strip():  # nur wenn nicht leer
            self.textWritten.emit(str(text))

    def flush(self):
        pass  # für Kompatibilität


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataminer by Unit 404")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.selected_dir = None
        self.thread = None
        self.worker = None

        self.setObjectName("mainWindow")

        layout = QVBoxLayout(self)

        # Directory row
        dir_row = QHBoxLayout()

        self.pick_btn = QPushButton()
        self.pick_btn.clicked.connect(self.pick_directory)
        self.pick_btn.setFixedSize(256, 96)
        self.pick_btn.setObjectName("selectFolderButton")
        # with open("styles/testbutton.qss", "r", encoding="utf-8") as f:
        #    self.pick_btn.setStyleSheet(f.read())

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

        # Start Button
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("startButton")
        self.start_btn.setFixedSize(256, 96)
        self.start_btn.clicked.connect(self.start_processing)

        # Exit Button
        self.exit_btn = QPushButton()
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setObjectName("exitButton")
        self.exit_btn.setFixedSize(64, 64)

        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.exit_btn)
        layout.addLayout(action_row)

        self.resize(800, 640)

        # CSS laden
        self.apply_styles()

    def apply_styles(self):
        # add others as needed
        files = ["styles/main.qss", "styles/buttons.qss"]
        # files = ["styles/buttons.qss"]
        css = ""
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as h:
                    css += h.read() + "\n"
            except FileNotFoundError:
                print(f"⚠️ Stylesheet not found: {f}")
        self.setStyleSheet(css)

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

        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")
        self.start_btn.setEnabled(False)
        self.pick_btn.setEnabled(False)

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(lambda: self.worker.run(self.selected_dir))
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

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

    def show_help(self):
        self.help_window = HelpWindow()
        self.help_window.show()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
