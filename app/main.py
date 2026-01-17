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
    QFileDialog,
    QLineEdit,
    QTextEdit,
    QProgressBar,
    QCheckBox,
    QMessageBox,
)

from PySide6.QtCore import Qt, QThread, QEvent
from PySide6.QtGui import QIcon, QMouseEvent
import sys
import importlib.util
import subprocess
import os
from pathlib import Path

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent.parent
    
    return base_path / relative_path

# Add converter directory to path so we can import bigman
sys.path.insert(0, str(Path(__file__).parent.parent / "converter"))




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
        css_path = get_resource_path(css_file_path)
        with open(css_path, 'r') as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
        print(f"✅ Loaded stylesheet from {css_path}")
    except FileNotFoundError:
        print(f"❌ Stylesheet file not found: {css_file_path}")
    except Exception as e:
        print(f"❌ Error loading stylesheet: {e}")


class HelpWindow(QMainWindow):
    """Custom help window with neomorphism styling and custom title bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window flags for custom title bar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Drag functionality variables
        self.drag_position = None
        self.is_dragging = False

        # Create custom title bar
        title_layout = self._create_title_bar()

        # Window title
        title_label = QLabel("Help - Unit404 Dataminer")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("""
            QLabel#title_label {
                color: #4a4a4a;
                font-weight: 600;
                font-size: 14px;
                padding: 0px 15px;
                background: transparent;
            }
        """)
        
        # Window controls
        minimize_button = QPushButton("─")
        minimize_button.setObjectName("window_control minimize")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        
        maximize_button = QPushButton("□")
        maximize_button.setObjectName("window_control maximize")
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self._toggle_maximize)
        
        close_button = QPushButton("✕")
        close_button.setObjectName("window_control close")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        
        # Add to layout
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(maximize_button)
        title_layout.addWidget(close_button)
        
        self.title_bar.setLayout(title_layout)
        
        # Create content widget
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.title_bar)

        # Help content
        help_label = QLabel("How can we help you?")
        help_label.setObjectName("help_title")
        help_label.setStyleSheet("""
            QLabel#help_title {
                color: #4a4a4a;
                font-weight: 600;
                font-size: 16px;
                padding: 20px;
                background: transparent;
            }
        """)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        tutorial_button = QPushButton("View Tutorial")
        tutorial_button.setObjectName("help_button")
        tutorial_button.clicked.connect(self.open_tutorial)
        
        email_button = QPushButton("Email Support")
        email_button.setObjectName("help_button")
        email_button.clicked.connect(self.open_email)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("help_button")
        cancel_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(tutorial_button)
        button_layout.addWidget(email_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        
        layout.addWidget(help_label)
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Store parent reference for tutorial
        self.parent_window = parent

    def _create_title_bar(self):
        """Create custom title bar for dragging."""
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        return title_layout

    def _toggle_maximize(self):
        """Toggle between maximize and restore."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def open_tutorial(self):
        """Open tutorial window."""
        if self.parent_window:
            self.parent_window.open_tutorial_window()
        self.close()

    def open_email(self):
        """Open email client."""
        import subprocess
        try:
            subprocess.run(["open", "mailto:unit@404.net"])
        except:
            print("Could not open email client")
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if self.is_dragging and self.drag_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_position
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.drag_position = None


class LogFileWindow(QMainWindow):
    """Window to display the statfile content."""

    def __init__(self, statfile_path):
        super().__init__()
        self.setWindowTitle("Log File Viewer")
        self.setGeometry(200, 200, 600, 400)
        
        # Set window flags for proper behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Drag functionality variables
        self.drag_position = None
        self.is_dragging = False

        # Create custom title bar
        title_layout = self._create_title_bar()

        # Window title
        title_label = QLabel("Log File Viewer")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("""
            QLabel#title_label {
                color: #4a4a4a;
                font-weight: 600;
                font-size: 14px;
                padding: 0px 15px;
                background: transparent;
            }
        """)
        
        # Window controls
        minimize_button = QPushButton("─")
        minimize_button.setObjectName("window_control minimize")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        
        maximize_button = QPushButton("□")
        maximize_button.setObjectName("window_control maximize")
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self._toggle_maximize)
        
        close_button = QPushButton("✕")
        close_button.setObjectName("window_control close")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        
        # Add to layout
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(maximize_button)
        title_layout.addWidget(close_button)
        
        self.title_bar.setLayout(title_layout)
        
        # Create content widget
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.title_bar)

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

        layout.addWidget(text_display)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _create_title_bar(self):
        """Create custom title bar for dragging."""
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        return title_layout

    def _toggle_maximize(self):
        """Toggle between maximize and restore."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if self.is_dragging and self.drag_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_position
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.drag_position = None


class TutorialWindow(QMainWindow):
    """Window to display the tutorial."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutorial")
        self.setGeometry(250, 250, 700, 500)
        
        # Set window flags for rounded corners, no menu bar, and drag functionality
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Drag functionality variables
        self.drag_position = None
        self.is_dragging = False

        # Create custom title bar
        title_layout = self._create_title_bar()

        # Window title
        title_label = QLabel("Tutorial")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("""
            QLabel#title_label {
                color: #4a4a4a;
                font-weight: 600;
                font-size: 14px;
                padding: 0px 15px;
                background: transparent;
            }
        """)
        
        # Window controls
        minimize_button = QPushButton("─")
        minimize_button.setObjectName("window_control minimize")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        
        maximize_button = QPushButton("□")
        maximize_button.setObjectName("window_control maximize")
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self._toggle_maximize)
        
        close_button = QPushButton("✕")
        close_button.setObjectName("window_control close")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        
        # Add to layout
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(maximize_button)
        title_layout.addWidget(close_button)
        
        self.title_bar.setLayout(title_layout)
        
        # Create content widget
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.title_bar)
        
        # Create text display
        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setObjectName("tutorial_display")

        tutorial_text = """Welcome to the Unit404 Dataminer App Tutorial!

1. Select Folder:
   Click the 'Select Folder' button to choose a directory containing audio files (.wav)
   that you want to convert to text and then to PDF.

2. Start Processing:
   Once a folder is selected, click the 'Start' button to begin the conversion process.
   The app will:
   - Convert audio files to text using the first progress bar
   - Convert the generated text files to PDF using the second progress bar

3. Monitor Progress:
   - The first progress bar shows audio-to-text conversion progress
   - The second progress bar shows text-to-PDF conversion progress
   - Console output displays detailed processing information

4. View Results:
   - Text files are saved in 'txtfiles_*' directories
   - PDF files are saved in 'pdfs_*' directories
   - Click 'Show Log File' to view processing statistics

5. Cleanup:
   - Click the 'Cleanup' button to remove all generated files and directories
   - This will delete all txt, pdf, and log files

For more help, click the '?' button in the top-right corner or access the Help menu."""
        text_display.setText(tutorial_text)

        layout.addWidget(text_display)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _toggle_maximize(self):
        """Toggle between maximize and restore."""
        if self.isMaximized():
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def _create_title_bar(self):
        """Create custom title bar for dragging."""
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        return title_layout

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if self.is_dragging and self.drag_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_position
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.drag_position = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window flags for custom title bar, rounded corners, and no menu bar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window attributes for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Drag functionality variables
        self.drag_position = None
        self.is_dragging = False
        
        # Initialize UI
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
        
        # Create custom title bar
        # Create menubar
        self._create_menubar()

        # Create central widget and layout
        main_widget = QWidget()
        main_widget.setObjectName("main_widget")
        
        # Main layout with title bar
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create custom title bar
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Window title
        title_label = QLabel("Dataminer App")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("""
            QLabel#title_label {
                color: #4a4a4a;
                font-weight: 600;
                font-size: 14px;
                padding: 0px 15px;
                background: transparent;
            }
        """)
        
        # Window controls
        minimize_button = QPushButton("─")
        minimize_button.setObjectName("window_control minimize")
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        
        maximize_button = QPushButton("□")
        maximize_button.setObjectName("window_control maximize")
        maximize_button.setFixedSize(30, 30)
        maximize_button.clicked.connect(self._toggle_maximize)
        
        close_button = QPushButton("✕")
        close_button.setObjectName("window_control close")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        
        # Add to layout
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(maximize_button)
        title_layout.addWidget(close_button)
        
        self.title_bar.setLayout(title_layout)
        
        # Store maximize state
        self.is_maximized = False
        
        # Create content widget
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        
        layout = QVBoxLayout()
        
        # Window controls bar
        controls_bar = QWidget()
        controls_bar.setObjectName("controls_bar")
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)
        
        # Window title text
        title_label = QLabel("Unit404 Dataminer")
        title_label.setObjectName("window_title")
        title_label.setStyleSheet("""
            QLabel#window_title {
                color: #000000;
                font-weight: bold;
                font-size: 14px;
                padding: 0px 10px;
                background: transparent;
            }
        """)
        
        # Window controls
        minimize_button = QPushButton("─")
        minimize_button.setObjectName("window_control minimize")
        minimize_button.setFixedSize(25, 20)
        minimize_button.setStyleSheet("color: #000000; font-weight: bold;")
        minimize_button.clicked.connect(self.showMinimized)
        
        maximize_button = QPushButton("□")
        maximize_button.setObjectName("window_control maximize")
        maximize_button.setFixedSize(25, 20)
        maximize_button.setStyleSheet("color: #000000; font-weight: bold;")
        maximize_button.clicked.connect(self._toggle_maximize)
        
        close_button = QPushButton("✕")
        close_button.setObjectName("window_control close")
        close_button.setFixedSize(25, 20)
        close_button.setStyleSheet("color: #000000; font-weight: bold;")
        close_button.clicked.connect(self.close)
        
        # Add controls to layout
        controls_layout.addWidget(title_label)
        controls_layout.addStretch()
        
        # Help button
        help_button = QPushButton("?")
        help_button.setObjectName("window_control help")
        help_button.setFixedSize(25, 20)
        help_button.clicked.connect(self.show_help_dialog)
        help_button.setStyleSheet("color: #000000; font-weight: bold;")
        
        controls_layout.addWidget(help_button)
        controls_layout.addWidget(minimize_button)
        controls_layout.addWidget(maximize_button)
        controls_layout.addWidget(close_button)
        
        controls_bar.setLayout(controls_layout)
        
        # Enable mouse tracking for drag functionality
        self.setMouseTracking(True)
        controls_bar.setMouseTracking(True)
        
        layout.addWidget(controls_bar)
        
        # Tutorial link at the top
        self.tutorial_link = QLabel("Tutorial")
        self.tutorial_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tutorial_link.setObjectName("tutorial_link")
        self.tutorial_link.setStyleSheet(
            "color: #000000; text-decoration: underline; font-weight: bold;")
        self.tutorial_link.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Install event filter to handle clicks without overriding mousePressEvent
        self.tutorial_link.installEventFilter(self)
        
        layout.addWidget(self.tutorial_link)

        # Top row: Select folder and Start buttons
        self.top_buttons_layout = QHBoxLayout()

        # Select folder button
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.setObjectName("select_folder_button")
        self.select_folder_button.clicked.connect(self.on_select_folder)
        self.top_buttons_layout.addWidget(self.select_folder_button)

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.on_start)
        self.start_button_enabled = False
        self._update_start_button_state()
        self.top_buttons_layout.addWidget(self.start_button)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.on_stop)
        self.stop_button.setEnabled(False)
        self.top_buttons_layout.addWidget(self.stop_button)

        layout.addLayout(self.top_buttons_layout)

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

        # File type selection checkboxes (will be populated after directory selection)
        self.file_types_label = QLabel("File Types to Convert:")
        self.file_types_label.setObjectName("file_types_label")
        self.file_types_label.setStyleSheet("color: #333333; font-weight: bold;")
        layout.addWidget(self.file_types_label)

        self.file_types_layout = QHBoxLayout()
        self.file_type_checkboxes = {}
        layout.addLayout(self.file_types_layout)

        # Console output display
        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)
        self.console_display.setObjectName("console_display")
        self.console_display.setMaximumHeight(150)
        layout.addWidget(self.console_display)

        # Progress bar
        # Progress bar label 1
        self.progress_label_1 = QLabel("Converting files to text")
        self.progress_label_1.setObjectName("progress_label_1")
        self.progress_label_1.setStyleSheet("color: #333333;")
        self.progress_label_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.progress_label_1)

        # Progress bar 1
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar_1")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Progress bar label 2
        self.progress_label_2 = QLabel("Converting text to PDF")
        self.progress_label_2.setObjectName("progress_label_2")
        self.progress_label_2.setStyleSheet("color: #333333;")
        self.progress_label_2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.progress_label_2)

        # Progress bar 2
        self.progress_bar_2 = QProgressBar()
        self.progress_bar_2.setObjectName("progress_bar_2")
        self.progress_bar_2.setMinimum(0)
        self.progress_bar_2.setMaximum(100)
        self.progress_bar_2.setValue(0)
        layout.addWidget(self.progress_bar_2)

        # Bottom row: Show log file, Cleanup, and Exit buttons
        self.bottom_buttons_layout = QHBoxLayout()

        # Show log file button
        self.show_log_button = QPushButton("Show Log File")
        self.show_log_button.setObjectName("show_log_button")
        self.show_log_button.clicked.connect(self.on_show_log_file)
        self.bottom_buttons_layout.addWidget(self.show_log_button)

        # Cleanup button
        self.cleanup_button = QPushButton("Cleanup")
        self.cleanup_button.setObjectName("cleanup_button")
        self.cleanup_button.clicked.connect(self.on_cleanup)
        self.bottom_buttons_layout.addWidget(self.cleanup_button)

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setObjectName("exit_button")
        self.exit_button.clicked.connect(self.on_exit)
        self.bottom_buttons_layout.addWidget(self.exit_button)

        layout.addLayout(self.bottom_buttons_layout)

        central_widget.setLayout(layout)
        main_layout.addWidget(central_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _update_start_button_state(self):
        """Update the start button appearance based on directory selection."""
        if self.start_button_enabled:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def _update_button_states(self, is_processing):
        """Update button states based on processing status."""
        self.start_button.setEnabled(not is_processing)
        self.stop_button.setEnabled(is_processing)
        if is_processing:
            self.start_button_enabled = False

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

    def _toggle_maximize(self):
        """Toggle between maximize and restore."""
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

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
            print(f"Starting file conversion with directory: {directory_path}")
            try:
                # Run bigman in a background thread to keep UI responsive
                bigman_path = Path(__file__).parent.parent / \
                    "converter" / "bigman.py"
                # Get selected file types
                selected_file_types = [
                    file_type for file_type, checkbox in self.file_type_checkboxes.items()
                    if checkbox.isChecked()
                ]
                self.worker_thread = WorkerThread(
                    str(bigman_path), "main", args=(directory_path, selected_file_types))
                # Disable start button and enable stop button while worker runs
                self._update_button_states(True)

                def _on_finished():
                    # Re-enable start button and disable stop button
                    self._update_button_states(False)
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

    def on_stop(self):
        """Handle stop button click - interrupt the running process."""
        if hasattr(self, 'worker_thread') and self.worker_thread.isRunning():
            self.status_label.setText("Stopping process...")
            print("Stopping worker thread...")
            
            # Terminate the worker thread
            self.worker_thread.terminate()
            self.worker_thread.wait(3000)  # Wait up to 3 seconds for thread to finish
            
            # Update UI state
            self._update_button_states(False)
            self.status_label.setText("Process stopped by user")
            print("Process stopped successfully")

    def on_exit(self):
        """Handle exit button click."""
        QApplication.quit()

    def on_show_log_file(self):
        """Handle show log file button click."""
        statfile_path = Path(__file__).parent.parent / "statfile.txt"
        print(f"Opening log file: {statfile_path}")
        self.log_window = LogFileWindow(statfile_path)
        self.log_window.show()

    def show_help_dialog(self):
        """Show help dialog with tutorial and email options."""
        self.help_window = HelpWindow(self)
        self.help_window.show()

    def open_tutorial_window(self):
        """Open tutorial window."""
        self.tutorial_window = TutorialWindow()
        self.tutorial_window.show()

    def eventFilter(self, obj, event):
        """Handle events for tutorial link and specific window interactions."""
        # Handle tutorial link click
        if obj == self.tutorial_link and event.type() == QEvent.Type.MouseButtonPress:
            self.tutorial_window = TutorialWindow()
            self.tutorial_window.show()
            return True
        
        # Don't interfere with other events
        return super().eventFilter(obj, event)

    def on_cleanup(self):
        """Handle cleanup button click - execute cleanup.sh script."""
        cleanup_script = Path(__file__).parent.parent / "setup" / "cleanup.sh"
        self.status_label.setText("Running cleanup...")
        print(f"Executing cleanup script: {cleanup_script}")
        try:
            subprocess.run(["bash", str(cleanup_script)], check=True)
            self.status_label.setText("Cleanup completed!")
            print("Cleanup completed successfully")
        except subprocess.CalledProcessError as e:
            self.status_label.setText(f"Cleanup error: {str(e)}")
            print(f"Cleanup script error: {e}")
        except Exception as e:
            self.status_label.setText(f"Error running cleanup: {str(e)}")
            print(f"Error running cleanup script: {e}")

    def _update_file_type_checkboxes(self, folder_path):
        """Scan folder, detect all file types, and create checkboxes dynamically."""
        # Scan for file types in the directory
        file_types_found = set()
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext:  # Only add if file has an extension
                        file_types_found.add(file_ext)
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return

        # Clear existing checkboxes
        for checkbox in self.file_type_checkboxes.values():
            checkbox.deleteLater()
        self.file_type_checkboxes.clear()

        # Create checkboxes only for file types found in directory
        if file_types_found:
            for i, file_type in enumerate(sorted(file_types_found)):
                # Display name is the file extension without the dot, uppercase
                display_name = file_type.lstrip('.').upper()
                checkbox = QCheckBox(display_name)
                checkbox.setObjectName(f"file_type_checkbox_{i}")
                checkbox.setChecked(True)  # All selected by default
                checkbox.setStyleSheet("color: #333333;")
                self.file_type_checkboxes[file_type] = checkbox
                self.file_types_layout.addWidget(checkbox)
            print(f"Found file types: {', '.join(sorted(file_types_found))}")
        else:
            # No files found
            self.no_files_label = QLabel("No files found in directory")
            self.no_files_label.setObjectName("no_files_label")
            self.no_files_label.setStyleSheet("color: #999999;")
            self.file_types_layout.addWidget(self.no_files_label)
            print("No files found in directory")

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
            self._update_file_type_checkboxes(folder_path)
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

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging."""
        if self.is_dragging and self.drag_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_position
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.drag_position = None


def main():
    app = QApplication(sys.argv)
    
    # Set application info to prevent "Python" in menu bar
    app.setApplicationName("Unit404 Dataminer")
    app.setOrganizationName("Unit404")
    app.setOrganizationDomain("unit404.dataminer")
    
    # Set application icon
    icon_path = get_resource_path("assets/logo.png")
    app.setWindowIcon(QIcon(str(icon_path)))
    
    # Load stylesheet from CSS file
    load_stylesheet(app, "styles/main.css")

    window = MainWindow()
    window.show()
    
    # Install event filter on the application to catch tutorial link events
    app.installEventFilter(window)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
