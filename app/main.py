from PySide6.QtCore import QObject, Signal
import progress
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMenu,
    QFileDialog,
    QLineEdit,
    QTextEdit,
    QProgressBar,
)
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, QSize, QEvent, QThread
import sys
import importlib.util
from pathlib import Path

# Add converter directory to path so we can import bigman
sys.path.insert(0, str(Path(__file__).parent.parent / "converter"))


class WorkerThread(QThread):
    """Run a converter module function in a background thread."""

    def __init__(self, module_path, func_name, args=()):
        super().__init__()
        self.module_path = module_path
        self.func_name = func_name
        self.args = args
        self.exception = None

    def run(self):
        try:
            spec = importlib.util.spec_from_file_location(
                "worker_module", self.module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            func = getattr(module, self.func_name)
            func(*self.args)
        except Exception as e:
            self.exception = e
            import traceback
            traceback.print_exc()


class ConsoleRedirector(QObject):
    """Redirects print statements to a QTextEdit widget using a Qt signal.

    Emitting a signal ensures text is appended on the GUI thread even when
    print() is called from a worker thread.
    """

    new_text = Signal(str)

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.original_stdout = sys.stdout
        # Connect the signal to the QTextEdit.append slot (runs on GUI thread)
        self.new_text.connect(self.text_edit.append)

    def write(self, message):
        """Write message to text edit and original stdout."""
        if message.strip():  # Only add non-empty messages
            self.new_text.emit(message)
        self.original_stdout.write(message)

    def flush(self):
        """Flush method for compatibility."""
        pass


def load_stylesheet(app, css_file_path):
    """Load and apply stylesheet from CSS file."""
    try:
        with open(css_file_path, 'r') as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    except FileNotFoundError:
        print(f"Warning: Stylesheet file not found: {css_file_path}")


class LogFileWindow(QMainWindow):
    """Window to display the statfile content."""

    def __init__(self, statfile_path):
        super().__init__()
        self.setWindowTitle("Log File Viewer")
        self.setGeometry(200, 200, 600, 400)

        # Create text display
        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setObjectName("log_display")

        # Read and display statfile content
        try:
            with open(statfile_path, 'r') as f:
                content = f.read()
            text_display.setText(content)
        except FileNotFoundError:
            text_display.setText(f"File not found: {statfile_path}")
        except Exception as e:
            text_display.setText(f"Error reading file: {str(e)}")

        self.setCentralWidget(text_display)


class HoverButton(QPushButton):
    """Custom button that changes appearance on hover."""

    def __init__(self, button_name, assets_dir, width=200, height=100):
        super().__init__()
        self.button_name = button_name
        self.assets_dir = assets_dir
        self.normal_pixmap = None
        self.hover_pixmap = None

        self.setFlat(True)
        self.setFixedSize(width, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Remove focus rectangle
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setObjectName("hover_button")

        # Load pixmaps
        normal_path = self.assets_dir / f"{button_name}_NORMAL.png"
        hover_path = self.assets_dir / f"{button_name}_HOVER.png"

        if normal_path.exists():
            self.normal_pixmap = QPixmap(str(normal_path))
        if hover_path.exists():
            self.hover_pixmap = QPixmap(str(hover_path))

        # Set initial icon
        if self.normal_pixmap:
            icon = QIcon(self.normal_pixmap)
            self.setIcon(icon)
            self.setIconSize(QSize(width, height))

    def enterEvent(self, event: QEvent):
        """Handle mouse enter event."""
        if self.hover_pixmap and self.isEnabled():
            self.setIcon(QIcon(self.hover_pixmap))
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """Handle mouse leave event."""
        if self.normal_pixmap:
            self.setIcon(QIcon(self.normal_pixmap))
        super().leaveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get the assets directory path relative to this file
        self.assets_dir = Path(__file__).parent.parent / "assets"
        self.init_ui()

        # Register this window with the global progress system
        progress.set_progress_window(self)

        # Redirect console output to the text display
        self.console_output = ConsoleRedirector(self.console_display)
        sys.stdout = self.console_output

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Dataminer App")
        self.setGeometry(100, 100, 400, 300)

        # Create menubar
        self._create_menubar()

        # Create central widget and layout
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Top row: Select folder and Start buttons
        top_buttons_layout = QHBoxLayout()

        # Select folder button with hover effect
        self.select_folder_button = HoverButton(
            "select_folder", self.assets_dir)
        self.select_folder_button.clicked.connect(self.on_select_folder)
        top_buttons_layout.addWidget(self.select_folder_button)

        # Start button with hover effect
        self.start_button = HoverButton("start", self.assets_dir)
        self.start_button.clicked.connect(self.on_start)
        self.start_button_enabled = False
        self._update_start_button_state()
        top_buttons_layout.addWidget(self.start_button)

        layout.addLayout(top_buttons_layout)

        # Status label
        self.status_label = QLabel("Ready to start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)

        # Selected directory display field
        self.directory_field = QLineEdit()
        self.directory_field.setReadOnly(True)
        self.directory_field.setPlaceholderText("No directory selected")
        self.directory_field.setObjectName("directory_field")
        layout.addWidget(self.directory_field)

        # Console output display
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        self.console_display.setObjectName("console_display")
        self.console_display.setMaximumHeight(150)
        layout.addWidget(self.console_display)

        # Progress bar
        # Progress bar label 1
        self.progress_label_1 = QLabel("Converting files to text")
        self.progress_label_1.setObjectName("progress_label")
        # Ensure label is visible regardless of global stylesheet
        self.progress_label_1.setStyleSheet("color: #333333;")
        self.progress_label_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.progress_label_1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)

        # Progress bar label 2
        self.progress_label_2 = QLabel("Converting text to PDF")
        self.progress_label_2.setObjectName("progress_label")
        # Ensure label is visible regardless of global stylesheet
        self.progress_label_2.setStyleSheet("color: #333333;")
        self.progress_label_2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.progress_label_2)

        # Second progress bar
        self.progress_bar_2 = QProgressBar()
        self.progress_bar_2.setObjectName("progress_bar")
        self.progress_bar_2.setMinimum(0)
        self.progress_bar_2.setMaximum(100)
        self.progress_bar_2.setValue(0)
        self.progress_bar_2.setMinimumHeight(25)
        layout.addWidget(self.progress_bar_2)

        # Bottom row: Show log file and Exit buttons
        bottom_buttons_layout = QHBoxLayout()

        # Show log file button with hover effect
        self.show_log_button = HoverButton("show_log_file", self.assets_dir)
        self.show_log_button.clicked.connect(self.on_show_log_file)
        bottom_buttons_layout.addWidget(self.show_log_button)

        # Exit button with hover effect
        self.exit_button = HoverButton(
            "close_button", self.assets_dir, width=100, height=50)
        self.exit_button.clicked.connect(self.on_exit)
        bottom_buttons_layout.addWidget(self.exit_button)

        layout.addLayout(bottom_buttons_layout)

        central_widget.setLayout(layout)

    def _update_start_button_state(self):
        """Update the start button appearance based on directory selection."""
        if self.start_button_enabled:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def set_progress(self, value):
        """Set the progress bar value (0-100)."""
        self.progress_bar.setValue(int(value))
        QApplication.processEvents()

    def reset_progress(self):
        """Reset the progress bar to 0."""
        self.progress_bar.setValue(0)
        QApplication.processEvents()

    def set_progress_2(self, value):
        """Set the second progress bar value (0-100)."""
        self.progress_bar_2.setValue(int(value))
        QApplication.processEvents()

    def reset_progress_2(self):
        """Reset the second progress bar to 0."""
        self.progress_bar_2.setValue(0)
        QApplication.processEvents()

    def _create_menubar(self):
        """Create the application menubar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.on_file_new)
        file_menu.addAction("Open", self.on_file_open)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.on_exit)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.on_help_about)
        help_menu.addAction("Documentation", self.on_help_documentation)

        # License menu
        license_menu = menubar.addMenu("License")
        license_menu.addAction("View License", self.on_license_view)
        license_menu.addAction("License Info", self.on_license_info)

    def on_start(self):
        """Handle start button click."""
        directory_path = self.directory_field.text()
        if directory_path and Path(directory_path).exists():
            self.status_label.setText("Processing started...")
            self.reset_progress()
            self.reset_progress_2()
            # Reset internal progress counters in shared progress module
            try:
                progress.set_progress(0)
                progress.set_progress_2(0)
            except Exception:
                pass
            print(f"Starting bigman with directory: {directory_path}")
            try:
                # Run bigman in a background thread to keep UI responsive
                bigman_path = Path(__file__).parent.parent / \
                    "converter" / "bigman.py"
                self.worker_thread = WorkerThread(
                    str(bigman_path), "main", args=(directory_path,))
                # Disable start button while worker runs
                self.start_button.setEnabled(False)

                def _on_finished():
                    # Re-enable start button
                    self.start_button.setEnabled(True)
                    if getattr(self.worker_thread, 'exception', None):
                        self.status_label.setText(
                            f"Error: {str(self.worker_thread.exception)}")
                        print(
                            f"Error occurred: {self.worker_thread.exception}")
                    else:
                        self.status_label.setText("Processing completed!")

                self.worker_thread.finished.connect(_on_finished)
                self.worker_thread.start()
            except Exception as e:
                self.status_label.setText(f"Error starting worker: {str(e)}")
                print(f"Error starting worker: {e}")
        else:
            self.status_label.setText("No valid directory selected")

    def on_exit(self):
        """Handle exit button click."""
        self.close()

    def on_show_log_file(self):
        """Handle show log file button click."""
        statfile_path = Path(__file__).parent.parent / "statfile.txt"
        print(f"Opening log file: {statfile_path}")
        self.log_window = LogFileWindow(statfile_path)
        self.log_window.show()

    def on_select_folder(self):
        """Handle select folder button click."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select a Folder",
            "",
            options=QFileDialog.Option.ShowDirsOnly
        )
        if folder_path:
            self.status_label.setText(f"Selected: {folder_path}")
            self.directory_field.setText(folder_path)
            self.start_button_enabled = True
            self._update_start_button_state()
            print(f"Folder selected: {folder_path}")
        else:
            self.status_label.setText("No folder selected")
            self.directory_field.clear()
            print("Folder selection cancelled")

    def on_file_new(self):
        """Handle File > New action."""
        self.status_label.setText("New file created")
        print("New file action triggered")

    def on_file_open(self):
        """Handle File > Open action."""
        self.status_label.setText("Opening file...")
        print("Open file action triggered")

    def on_help_about(self):
        """Handle Help > About action."""
        self.status_label.setText("About Dataminer")
        print("About action triggered")

    def on_help_documentation(self):
        """Handle Help > Documentation action."""
        self.status_label.setText("Opening documentation...")
        print("Documentation action triggered")

    def on_license_view(self):
        """Handle License > View License action."""
        self.status_label.setText("Viewing license...")
        print("View license action triggered")

    def on_license_info(self):
        """Handle License > License Info action."""
        self.status_label.setText("License information displayed")
        print("License info action triggered")


def main():
    app = QApplication(sys.argv)

    # Load stylesheet from CSS file
    css_path = Path(__file__).parent.parent / "styles" / "main.css"
    load_stylesheet(app, css_path)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
