import logging
from collections import defaultdict

from picsellia_cv_engine.core.data import (
    CocoDataset,
)
from picsellia_cv_engine.core.services.data.dataset.validator.common import (
    DatasetValidator,
)

logger = logging.getLogger("picsellia-engine")


class CocoClassificationDatasetValidator(DatasetValidator[CocoDataset]):
    def validate(self):
        """
        Validate the classification dataset.
        A classification dataset must have at least 2 classes and at least 1 image per class.

        Logs the number of images per class and any errors found.
        Raises:
            ValueError: If the classification dataset is not valid.
        """
        super().validate()  # Call common validations
        self._validate_labelmap()
        self._validate_coco_file()

        return self.dataset

    def _validate_labelmap(self):
        """
        Validate that the labelmap for the dataset is valid.
        A classification labelmap must have at least 2 classes.

        Raises:
            ValueError: If the labelmap for the dataset is not valid.
        """
        if len(self.dataset.labelmap) < 2:
            raise ValueError(
                f"Labelmap for dataset {self.dataset.name} is not valid. "
                f"A classification labelmap must have at least 2 classes. "
                f"Current labelmap is {self.dataset.labelmap}"
            )

    def _validate_coco_file(self):
        """
        Validate that each class in the classification dataset has at least 1 image using the COCO file.
        If a class has no images, the dataset is considered invalid.

        Raises:
            ValueError: If any class in the classification dataset has no images.
            FileNotFoundError: If the COCO file is not found.
            json.JSONDecodeError: If the COCO file is not a valid JSON.
        """
        # Create a mapping of category_id to category_name
        if not self.dataset.coco_data:
            raise FileNotFoundError(
                f"COCO file not found for dataset {self.dataset.name}"
            )
        category_map = {
            cat["id"]: cat["name"] for cat in self.dataset.coco_data["categories"]
        }

        # Count images per category
        images_per_category: dict[str, int] = defaultdict(int)
        empty_classes_list: list[str] = []

        for annotation in self.dataset.coco_data["annotations"]:
            category_name = category_map[annotation["category_id"]]
            images_per_category[category_name] += 1

        # Check if each class in the labelmap has at least one image
        for class_name in self.dataset.labelmap.keys():
            if images_per_category[class_name] == 0:
                empty_classes_list.append(class_name)

        self._log_image_count_per_class(images_per_category)

        # Check if there are any classes in the COCO file that are not in the labelmap
        coco_classes = set(category_map.values())
        labelmap_classes = set(self.dataset.labelmap.keys())
        extra_classes_list = list(coco_classes - labelmap_classes)

        if len(empty_classes_list) > 0 or len(extra_classes_list) > 0:
            self._log_and_raise_errors(
                empty_classes_list=empty_classes_list,
                extra_classes_list=extra_classes_list,
            )

    def _log_image_count_per_class(self, class_image_count):
        """
        Logs the number of images for each class in the dataset.
        """
        logger.info(f"Dataset '{self.dataset.name}' image distribution:")
        for class_name, count in class_image_count.items():
            logger.info(f" - Class '{class_name}': {count} images")

    def _log_and_raise_errors(
        self, empty_classes_list: list[str], extra_classes_list: list[str]
    ):
        """
        Logs the errors found during validation and raises a ValueError with the combined messages.
        """
        logger.error(
            f"Errors found during validation of the COCO file for the dataset {self.dataset.name}:"
        )

        for empty_class in empty_classes_list:
            logger.error(f"No images found for class '{empty_class}'")

        for extra_class in extra_classes_list:
            logger.error(
                f"Class '{extra_class}' is present in the COCO file but not in the labelmap"
            )

        raise ValueError(
            f"Validation failed with errors: {len(empty_classes_list)} classes have no images and "
            f"{len(extra_classes_list)} classes are not in the labelmap"
        )
