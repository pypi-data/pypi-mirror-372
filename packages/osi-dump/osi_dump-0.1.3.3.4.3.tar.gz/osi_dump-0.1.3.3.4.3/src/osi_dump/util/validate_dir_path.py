import os


def validate_dir_path(file_path: str):
    """
    Extracts the directory path from a file path and checks if it is valid.

    Args:
        file_path (str): The file path to extract the directory from.

    Returns:
        str: The directory path if it exists, otherwise an appropriate message.
    """
    # Extract the directory path
    dir_path = os.path.dirname(file_path)

    if not dir_path:
        return True
    # Check if the directory exists
    return os.path.exists(dir_path)
