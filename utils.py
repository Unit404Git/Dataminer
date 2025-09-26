import os


def organize_files_by_top_directories(root_directory=None):

    if not root_directory:
        print("No directory selected.")
        return {}

    # Dictionary to hold file lists for each top-level directory
    file_structure = {}

    # Iterate through the contents of the root directory
    for dir_name in os.listdir(root_directory):
        dir_path = os.path.join(root_directory, dir_name)

        if os.path.isdir(dir_path):  # Only process directories
            file_structure[dir_name] = []

            # Walk through the directory and collect file paths
            for subdirpath, _, filenames in os.walk(dir_path):
                for file in filenames:
                    file_structure[dir_name].append(
                        os.path.join(subdirpath, file))

    return file_structure
