from nicegui import ui, app
from processor import process_directory
from tkinter import Tk, filedialog  # <-- for native folder dialog

selected_dir = None
progress_bar = None
progress_label = None


def pick_dir():
    global selected_dir
    root = Tk()
    root.withdraw()  # hide the root window
    result = filedialog.askdirectory()
    root.destroy()
    if result:
        selected_dir = result
        chosen_label.set_text(f"Selected: {selected_dir}")


def start_processing():
    global selected_dir, progress_bar, progress_label
    if not selected_dir:
        ui.notify('Please select a directory first.', color='red')
        return

    # Reset UI progress
    progress_bar.set_value(0)
    progress_label.set_text("Starting...")

    # Run processing (this yields progress updates)
    total, progress_iter = process_directory(selected_dir)

    for i, message in enumerate(progress_iter, start=1):
        progress_bar.set_value(i / total)
        progress_label.set_text(message)

    progress_label.set_text("Done ✅")
    ui.notify('Processing finished!', color='green')


def quit_app():
    ui.run_javascript("window.close();")  # try to close the tab
    app.shutdown()  # stop NiceGUI


with ui.row():
    ui.label("Choose a directory to process:")

with ui.row():
    ui.button("Pick Directory", on_click=pick_dir)
    chosen_label = ui.label("No directory selected.")

progress_bar = ui.linear_progress(value=0)
progress_label = ui.label("Waiting to start...")

with ui.row():
    ui.button("Start", on_click=start_processing, color="green")
    ui.button("Exit", on_click=quit_app, color="red")

# auto-open browser
ui.run(host='127.0.0.1', port=8080)
