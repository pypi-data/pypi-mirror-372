import os
import shutil

from picsellia_annotations.coco import Image

from picsellia_cv_engine.core import CocoDataset


class ClassificationBaseDatasetPreparator:
    """
    Prepares and organizes dataset images into directories based on their classification categories.

    This class takes a dataset with category and annotation information in COCO format.
    It organizes the dataset by creating a directory for each category and moves the images into their
    respective category directories, which is often required for classification tasks in deep learning frameworks.

    Attributes:
        dataset (BaseDataset): The context of the dataset including paths and COCO file.
        destination_dir (str): The target directory where the images will be moved and organized.
    """

    def __init__(self, dataset: CocoDataset, destination_dir: str):
        """
        Initializes the preparator with a given dataset and a destination directory for images.

        Args:
            dataset (BaseDataset): The context of the dataset to organize.
            destination_dir (str): The directory where the organized images will be stored.

        Raises:
            ValueError: If the destination image directory is the same as the original image directory.
        """
        self.dataset = dataset
        self.destination_dir = destination_dir
        if self.dataset.images_dir == self.destination_dir:
            raise ValueError(
                "The destination image directory cannot be the same as the original image directory."
            )
        if not self.dataset.images_dir:
            raise ValueError("No images directory found in the dataset.")
        if not self.dataset.coco_data:
            raise ValueError("No COCO data loaded in the dataset.")

    def organize(self) -> CocoDataset:
        """
        Organizes the dataset by creating category directories and moving images.

        Extracts category information from the COCO file, maps images to their categories,
        and organizes the images into the respective category directories. Cleans up the original
        image directory and annotations directory after moving the images.

        Returns:
            CocoDataset: The updated dataset with the new image directory.
        """
        categories = self._extract_categories()
        image_categories = self._map_image_to_category()
        self._organize_images(categories, image_categories)

        # Remove the old images directory once images are moved
        if not self.dataset.images_dir:
            raise ValueError("No images directory found in the dataset.")
        shutil.rmtree(self.dataset.images_dir)
        self.dataset.images_dir = self.destination_dir

        return self.dataset

    def _extract_categories(self) -> dict[int, str]:
        """
        Extracts the categories from the dataset's COCO data.

        Returns:
            Dict[int, str]: A dictionary mapping category IDs to category names.
        """
        if not self.dataset.coco_data:
            raise ValueError("No COCO data loaded in the dataset.")
        return {
            category["id"]: category["name"]
            for category in self.dataset.coco_data.get("categories", [])
        }

    def _map_image_to_category(self) -> dict[int, int]:
        """
        Maps each image to its category based on the annotations in the COCO data.

        Returns:
            Dict[int, int]: A dictionary mapping image IDs to category IDs.
        """
        if not self.dataset.coco_data:
            raise ValueError("No COCO data loaded in the dataset.")
        return {
            annotation["image_id"]: annotation["category_id"]
            for annotation in self.dataset.coco_data.get("annotations", [])
        }

    def _organize_images(
        self, categories: dict[int, str], image_categories: dict[int, int]
    ) -> None:
        """
        Creates category directories and moves images into their respective directories.

        Args:
            categories (Dict[int, str]): A mapping from category IDs to category names.
            image_categories (Dict[int, int]): A mapping from image IDs to category IDs.
        """
        if not self.dataset.coco_data:
            raise ValueError("No COCO data loaded in the dataset.")
        for image in self.dataset.coco_data.get("images", []):
            image_id = image["id"]
            if image_id in image_categories:
                category_id = image_categories[image_id]
                category_name = categories[category_id]
                self._create_category_dir_and_copy_image(category_name, image)

    def _create_category_dir_and_copy_image(
        self, category_name: str, image: Image
    ) -> None:
        """
        Creates a directory for a category if it doesn't exist and moves an image into it.

        Args:
            category_name (str): The name of the category.
            image (Dict[str, Any]): The image object containing file name and metadata.

        Raises:
            PermissionError: If there is a permission issue when creating the directory or moving the file.
            FileNotFoundError: If the source image file is not found.
            shutil.SameFileError: If the source and destination paths are the same.
        """
        if not self.dataset.images_dir:
            raise ValueError("No images directory found in the dataset.")
        category_dir = os.path.join(self.destination_dir, category_name)
        os.makedirs(category_dir, exist_ok=True)
        src_image_path = os.path.join(self.dataset.images_dir, image["file_name"])
        dest_image_path = os.path.join(category_dir, image["file_name"])
        shutil.move(src_image_path, dest_image_path)
