import json
import logging

from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.services.data.dataset.validator import DatasetValidator

logger = logging.getLogger(__name__)


class CocoObjectDetectionDatasetValidator(DatasetValidator[CocoDataset]):
    def __init__(self, dataset: CocoDataset, fix_annotation=True):
        """
        Initialize the validator for a COCO object detection dataset.

        Args:
            dataset (CocoDataset): The dataset containing the COCO data to validate.
            fix_annotation (bool): Flag to indicate whether to automatically fix issues (default is True).

        Attributes:
            error_count (Dict): A dictionary to track the count of different types of errors found during validation.
        """
        super().__init__(dataset=dataset, fix_annotation=fix_annotation)
        self.error_count = {
            "top_left_x": 0,
            "top_left_y": 0,
            "bottom_right_x": 0,
            "bottom_right_y": 0,
        }

    def validate(self) -> CocoDataset:
        """
        Validate the COCO object detection dataset.

        Ensures the dataset has:
        - At least one class in the labelmap.
        - At least one image with bounding boxes.
        - Valid bounding box coordinates for all annotations.

        Returns:
            CocoDataset: The validated (or fixed) dataset.

        Raises:
            ValueError: If the dataset is invalid and `fix_annotation` is set to False.
        """
        super().validate()
        self._validate_labelmap()
        self._validate_at_least_one_image_with_bounding_boxes()
        self._validate_bounding_boxes_coordinates()

        if any(self.error_count.values()):
            self._report_errors()

        if self.fix_annotation:
            self._save_updated_coco_file()

        return self.dataset

    def _validate_labelmap(self):
        """
        Validate that the labelmap for the dataset is valid.

        An object detection labelmap must have at least one class to be considered valid.

        Raises:
            ValueError: If the labelmap does not contain at least one class.
        """
        if len(self.dataset.labelmap) < 1:
            raise ValueError(
                f"Labelmap for dataset {self.dataset.name} is not valid. "
                f"An object detection labelmap must have at least 1 class."
            )

    def _validate_at_least_one_image_with_bounding_boxes(self):
        """
        Validate that the dataset contains at least one image with bounding boxes.

        The dataset is considered invalid if there are no images with annotations containing bounding boxes.

        Raises:
            ValueError: If no images with bounding boxes are found in the dataset.
        """
        if not self.dataset.coco_data:
            raise ValueError(f"Dataset {self.dataset.name} has no COCO data loaded.")
        if not self.dataset.coco_data.get("annotations"):
            raise ValueError(
                f"Dataset {self.dataset.name} must have at least 1 image with bounding boxes."
            )

    def _validate_bounding_boxes_coordinates(self):
        """
        Validate the bounding box coordinates for all annotations in the dataset.

        Checks that:
        - Coordinates are greater than or equal to 0.
        - The bottom-right coordinates are greater than the top-left coordinates.

        Raises:
            ValueError: If any annotation has invalid bounding box coordinates and `fix_annotation` is False.
        """
        if not self.dataset.coco_data or "annotations" not in self.dataset.coco_data:
            raise ValueError(
                f"Dataset {self.dataset.name} has no annotations in COCO data."
            )
        for annotation in self.dataset.coco_data["annotations"]:
            modified_annotation = self._fix_or_count_errors(annotation)
            if modified_annotation:
                annotation["bbox"] = modified_annotation

    def _fix_or_count_errors(self, annotation: dict) -> list[float] | None:
        """
        Fix or count errors in the bounding box coordinates for a given annotation.

        Args:
            annotation (Dict): The annotation to validate, containing a 'bbox' field.

        Returns:
            Optional[List[float]]: If `fix_annotation` is True, returns the corrected bounding box [top_left_x, top_left_y, width, height].
                                      If there is no fix or `fix_annotation` is False, returns None.
        """
        x, y, width, height = annotation["bbox"]
        top_left_x, top_left_y = x, y
        bottom_right_x = x + width
        bottom_right_y = y + height
        image = self._get_image_by_id(annotation["image_id"])
        if not image:
            return None

        (
            top_left_x,
            top_left_y,
            bottom_right_x,
            bottom_right_y,
        ) = self._correct_coordinates_if_needed(
            top_left_x=top_left_x,
            top_left_y=top_left_y,
            bottom_right_x=bottom_right_x,
            bottom_right_y=bottom_right_y,
            image=image,
        )

        if self.fix_annotation:
            new_width = bottom_right_x - top_left_x
            new_height = bottom_right_y - top_left_y
            return [top_left_x, top_left_y, new_width, new_height]
        return None

    def _correct_coordinates_if_needed(
        self,
        top_left_x: int,
        top_left_y: int,
        bottom_right_x: int,
        bottom_right_y: int,
        image: dict,
    ) -> tuple[int, int, int, int]:
        """
        Correct the bounding box coordinates if they are invalid, based on image dimensions.

        Args:
            top_left_x (int): The x-coordinate of the top-left corner of the bounding box.
            top_left_y (int): The y-coordinate of the top-left corner of the bounding box.
            bottom_right_x (int): The x-coordinate of the bottom-right corner of the bounding box.
            bottom_right_y (int): The y-coordinate of the bottom-right corner of the bounding box.
            image (Dict): The image associated with the annotation, containing width and height.

        Returns:
            Tuple[int, int, int, int]: The corrected bounding box coordinates (top_left_x, top_left_y, bottom_right_x, bottom_right_y).

        """
        if top_left_x < 0:
            self.error_count["top_left_x"] += 1
            if self.fix_annotation:
                top_left_x = 0

        if top_left_y < 0:
            self.error_count["top_left_y"] += 1
            if self.fix_annotation:
                top_left_y = 0

        if bottom_right_x > image["width"] or bottom_right_x <= top_left_x:
            self.error_count["bottom_right_x"] += 1
            if self.fix_annotation:
                bottom_right_x = max(top_left_x + 1, image["width"])

        if bottom_right_y > image["height"] or bottom_right_y <= top_left_y:
            self.error_count["bottom_right_y"] += 1
            if self.fix_annotation:
                bottom_right_y = max(top_left_y + 1, image["height"])

        return top_left_x, top_left_y, bottom_right_x, bottom_right_y

    def _get_image_by_id(self, image_id: int) -> dict | None:
        """
        Retrieve the image object associated with a given image ID.

        Args:
            image_id (int): The ID of the image to retrieve.

        Returns:
            Dict: The image object associated with the given ID.

        Raises:
            ValueError: If the image ID is not found in the dataset.
        """
        if not self.dataset.coco_data or "images" not in self.dataset.coco_data:
            raise ValueError(f"Dataset {self.dataset.name} has no images in COCO data.")
        return next(
            image
            for image in self.dataset.coco_data["images"]
            if image["id"] == image_id
        )

    def _save_updated_coco_file(self):
        """
        Save the updated COCO data back to the original COCO file if `fix_annotation` is True.

        Raises:
            ValueError: If the COCO file path is not set.
            RuntimeError: If there is an error while saving the updated COCO file.
        """
        if not self.dataset.coco_file_path:
            raise ValueError(
                "COCO file path is not set. Cannot save updated annotations."
            )

        try:
            with open(self.dataset.coco_file_path, "w") as coco_file:
                json.dump(self.dataset.coco_data, coco_file, indent=4)
            logger.info(f"Updated COCO file saved to {self.dataset.coco_file_path}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to save updated COCO file to {self.dataset.coco_file_path}: {e}"
            ) from e

    def _report_errors(self):
        """
        Report the errors found during validation.

        Iterates over the error counts and prints the details of each error type.
        """
        logger.warning(f"⚠️ Found {sum(self.error_count.values())} bounding box issues:")
        for error_type, count in self.error_count.items():
            logger.info(f" - {error_type}: {count} issues")

        if self.fix_annotation:
            logger.info("🔧 Fixing these issues automatically...")
        else:
            raise ValueError(
                "Bounding box issues detected. Set 'fix_annotation' to True to automatically fix them."
            )
