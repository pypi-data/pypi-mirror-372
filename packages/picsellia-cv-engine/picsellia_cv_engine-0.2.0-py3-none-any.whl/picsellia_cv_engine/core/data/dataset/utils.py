import logging
import os

logger = logging.getLogger(__name__)


def remove_empty_directories(directory: str) -> None:
    """
    Recursively remove empty directories from a given directory.

    Args:
        directory (str): The root directory to clean.
    """
    for root, dirs, _files in os.walk(directory, topdown=False):
        for dir_ in dirs:
            dir_path = os.path.join(root, dir_)
            if not os.listdir(dir_path):  # Check if the directory is empty
                os.rmdir(dir_path)
                logger.info(f"Removed empty directory: {dir_path}")
