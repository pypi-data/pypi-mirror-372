from typing import Generic, TypeVar

from PIL import Image

from picsellia_cv_engine.core import BaseDataset
from picsellia_cv_engine.core.services.utils.image_file import get_images_path_list

TBaseDataset = TypeVar("TBaseDataset", bound=BaseDataset)


class DatasetValidator(Generic[TBaseDataset]):
    """
    Validates various aspects of a dataset.

    This class performs common validation tasks for datasets, including checking for image extraction
    completeness, image format, image corruption, and annotation integrity.

    Attributes:
        dataset (Dataset): The dataset to validate.
    """

    VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

    def __init__(self, dataset: TBaseDataset, fix_annotation: bool = False):
        """
        Initializes the DatasetValidator with a dataset to validate.

        Parameters:
            dataset (Dataset): The dataset to validate.
        """
        self.dataset = dataset
        self.fix_annotation = fix_annotation

    def validate(self):
        """
        Validates the dataset.
        """
        if self.dataset.images_dir:
            images_path_list = get_images_path_list(images_dir=self.dataset.images_dir)
            self.validate_images_extraction(images_path_list=images_path_list)
            self.validate_images_format(images_path_list=images_path_list)
            self.validate_images_corruption(images_path_list=images_path_list)
        else:
            raise ValueError(
                f"Image directory is missing from the dataset in {self.dataset.name} dataset"
            )

    def validate_images_extraction(self, images_path_list: list[str]) -> None:
        """
        Validates that the number of extracted images matches the expected number of assets.

        Args:
            images_path_list (List[str]): The list of image paths extracted from the dataset.

        Raises:
            ValueError: If the number of extracted images does not match the expected number of assets.
        """
        if self.dataset.assets is None:
            return

        if len(images_path_list) < len(self.dataset.assets):
            raise ValueError(
                f"Some images have not been extracted in the image directory: {self.dataset.images_dir}. "
                + f"There are {len(images_path_list)} images in the directory and {len(self.dataset.assets)} assets in the dataset."
            )
        if len(images_path_list) > len(self.dataset.assets):
            raise ValueError(
                f"There are more images than expected in the image directory: {self.dataset.images_dir}. "
                + f"There are {len(images_path_list)} images in the directory and {len(self.dataset.assets)} assets in the dataset."
            )

    def validate_images_format(self, images_path_list: list[str]) -> None:
        """
        Validates that all images in the dataset are in an expected format.

        Args:
            images_path_list (List[str]): The list of image paths extracted from the dataset.

        Raises:
            ValueError: If any image is not in one of the valid formats.
        """
        for image_path in images_path_list:
            if not image_path.lower().endswith(self.VALID_IMAGE_EXTENSIONS):
                raise ValueError(
                    f"Invalid image format for image {image_path} in {self.dataset.name} dataset. "
                    f"Valid image formats are {self.VALID_IMAGE_EXTENSIONS}"
                )

    def validate_images_corruption(self, images_path_list: list[str]) -> None:
        """
        Checks for corruption in the extracted images.

        Parameters:
            images_path_list (List[str]): The list of image paths extracted from the dataset.

        Raises:
            ValueError: If any of the images are found to be corrupted.
        """
        for image_path in images_path_list:
            try:
                with Image.open(image_path) as img:
                    img.verify()  # Verify that this is a valid image
            except Exception as e:
                raise ValueError(
                    f"Image {image_path} is corrupted in {self.dataset.name} dataset and cannot be used."
                ) from e
