import os
import base64
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tqdm import tqdm
import create_pdf_file
import utils


def main(root_directory):
    print("bigman in da house")

    file_struct = utils.organize_files_by_top_directories(root_directory)

    # for directory, files in file_struct.items():
    # file_paths = get_all_file_paths()
    cwd = os.getcwd()
    stat_file = f"{cwd}/statfile.txt"

    for directory, files in file_struct.items():

        dirpath = f"{cwd}/textfiles_{directory}"
        create_dir = os.path.isdir(dirpath)
        if not create_dir:
            os.system(f"mkdir txtfiles_{directory}")
        else:
            rm_cmd = f"rm -rf {cwd}/textfiles_{directory}"
            os.system(rm_cmd)
            os.system(f"mkdir txtfiles_{directory}")

        print(f"currently working on: {directory}")
        file_paths = []
        for file in files:
            file_paths.append(file)

        to_convert = len(file_paths)

        msg = f"files to convert found = {to_convert}"
        print(msg)

        total_data_size = 0
        chunk_size = 10000  # Adjust as needed
        for path in tqdm(file_paths):
            for i, chunk in enumerate(read_wav_in_chunks(path, chunk_size)):
                name, ext = os.path.splitext(path)
                new_file_path = f"{name}_{i}.txt"

                with open(new_file_path, "w", encoding="utf-8") as writer:
                    for data in chunk:
                        bytes = data.to_bytes(5, 'little')
                        encoded_data = base64.b64encode(bytes).decode('utf-8')
                        writer.write(str(encoded_data))
                    data_size = os.path.getsize(new_file_path)
                    total_data_size += data_size
                    cmd = f"mv {new_file_path} {cwd}/txtfiles_{directory}"
                    os.system(cmd)

        total_data_size = total_data_size/1048576
        with open(stat_file, "at") as statwriter:
            statwriter.write(
                f"{directory} --- contained {total_data_size}MB as txt\n")
        # print(f"Brudi das warn ganze: {total_data_size}MB")
    create_pdf_file.main(file_struct)


def read_wav_in_chunks(file_path, chunk_size=10000):
    """
    Reads a .wav file in binary mode in chunks of specified size.

    Args:
        file_path (str): Path to the .wav file.
        chunk_size (int): Size of each chunk in bytes.

    Yields:
        bytes: A chunk of binary data from the file.
    """
    try:
        with open(file_path, "rb") as wav_file:
            while chunk := wav_file.read(chunk_size):
                yield chunk
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")


def get_all_file_paths(folder_path):
    # Create a tkinter root window (hidden)
    root = Tk()
    root.withdraw()  # Hide the root window
    root.attributes('-topmost', True)  # Bring the dialog to the front

    # Open a dialog to select a folder
    folder_path = askdirectory(title="Select a Folder")

    if not folder_path:
        print("No folder selected.")
        return []

    # Walk through the directory and collect all file paths
    file_paths = []
    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            file_paths.append(os.path.join(dirpath, file))

    return file_paths


# if __name__ == "__main__":
    # root = Tk()
    # root.withdraw()  # Hide the root window
    # root.attributes('-topmost', True)  # Bring the dialog to the front
    # Open a dialog to select the root directory
    # root_directory = askdirectory(title="Select a Root Directory")

    # file_struct = utils.organize_files_by_top_directories(root_directory)
    # main(file_struct)
