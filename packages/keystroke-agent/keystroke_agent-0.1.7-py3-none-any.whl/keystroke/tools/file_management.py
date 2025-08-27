import os
from typing import List


def create_file(filepath: str, content: str = "") -> None:
    """
    Create a new file with the specified content.

    Args:
        filepath (str): Path to the file to create.
        content (str, optional): Content to write to the file. Defaults to "".
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def read_file(filepath: str) -> str:
    """
    Read the content of a file.

    Args:
        filepath (str): Path to the file to read.

    Returns:
        str: Content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def update_file(filepath: str, content: str, append: bool = False) -> None:
    """
    Update the content of a file.

    Args:
        filepath (str): Path to the file to update.
        content (str): Content to write or append.
        append (bool, optional): If True, append to the file; otherwise, overwrite. Defaults to False.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    mode = "a" if append else "w"
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(content)


def delete_file(filepath: str) -> None:
    """
    Delete a file.

    Args:
        filepath (str): Path to the file to delete.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    os.remove(filepath)


def file_exists(filepath: str) -> bool:
    """
    Check if a file exists.

    Args:
        filepath (str): Path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(filepath)


def rename_file(src: str, dst: str) -> None:
    """
    Rename a file.

    Args:
        src (str): Source file path.
        dst (str): Destination file path.

    Raises:
        FileNotFoundError: If the source file does not exist.
    """
    os.rename(src, dst)


def copy_file(src: str, dst: str) -> None:
    """
    Copy a file to a new location.

    Args:
        src (str): Source file path.
        dst (str): Destination file path.

    Raises:
        FileNotFoundError: If the source file does not exist.
    """
    from shutil import copy2

    copy2(src, dst)


def list_files(directory: str, recursive: bool = False) -> List[str]:
    """
    List all files in a directory.

    Args:
        directory (str): Path to the directory.
        recursive (bool, optional): If True, list files recursively. Defaults to False.

    Returns:
        List[str]: List of file paths.
    """
    files = []
    if recursive:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(dirpath, filename))
    else:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path):
                files.append(full_path)
    return files


def delete_all_files(directory: str, recursive: bool = False) -> None:
    """
    Delete all files in a directory.

    Args:
        directory (str): Path to the directory.
        recursive (bool, optional): If True, delete files recursively in subdirectories. Defaults to False.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    if recursive:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                os.remove(file_path)
    else:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path):
                os.remove(full_path)
