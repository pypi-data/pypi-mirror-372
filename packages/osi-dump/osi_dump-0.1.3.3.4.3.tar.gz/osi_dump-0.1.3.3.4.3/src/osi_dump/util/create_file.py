import os


def create_file(file_path: str):
    # Check if the file already exists
    if os.path.exists(file_path):
        # Delete the old file
        os.remove(file_path)

    # Create and write to the new file
    open(file_path, "x")
