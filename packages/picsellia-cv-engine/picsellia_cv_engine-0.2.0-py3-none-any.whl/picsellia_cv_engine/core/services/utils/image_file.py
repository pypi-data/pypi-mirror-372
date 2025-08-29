import os


def get_images_path_list(images_dir: str) -> list[str]:
    """
    Generates a list of all image file paths within a specified directory.

    Args:
        images_dir (str): The directory to search for image files.

    Returns:
        list[str]: A list containing the paths to all images found within the directory and its subdirectories.
    """
    images_path_list = []
    for root, _dirs, files in os.walk(images_dir):
        for file in files:
            images_path_list.append(os.path.join(root, file))
    return images_path_list
