import logging
import os

from picsellia_cv_engine.core import YoloDataset
from picsellia_cv_engine.core.services.data.dataset.validator import DatasetValidator

logger = logging.getLogger(__name__)


class YoloObjectDetectionDatasetValidator(DatasetValidator[YoloDataset]):
    """
    Validator for YOLO format annotations.
    """

    def __init__(self, dataset: YoloDataset, fix_annotation=True):
        """
        Initializes the YOLO object detection dataset validator.

        Args:
            dataset (YoloDataset): The context object containing dataset information and annotations.
            fix_annotation (bool): Flag indicating whether to automatically fix the detected issues.
        """
        super().__init__(dataset=dataset, fix_annotation=fix_annotation)
        self.error_count = {
            "class_id": 0,
            "x_center": 0,
            "y_center": 0,
            "width": 0,
            "height": 0,
        }

    def validate(self) -> YoloDataset:
        """
        Validates the YOLO object detection dataset.

        This method performs the following validation checks:
        - Verifies that the labelmap contains at least one class.
        - Validates the format and bounds of the YOLO annotations.
        - Reports any issues found during the validation process.

        Returns:
            YoloDataset: The validated or updated dataset.

        Raises:
            ValueError: If validation errors are found and `fix_annotation` is set to False.
        """
        super().validate()
        self._validate_labelmap()
        self._validate_yolo_annotations()
        if any(self.error_count.values()):
            self._report_errors()
        return self.dataset

    def _validate_labelmap(self):
        """
        Validates the labelmap of the dataset.

        Ensures that the labelmap contains at least one class ID.

        Raises:
            ValueError: If the labelmap is empty or contains no classes.
        """
        if len(self.dataset.labelmap) < 1:
            raise ValueError(
                f"Labelmap for dataset {self.dataset.name} is not valid. "
                f"A YOLO labelmap must have at least 1 class."
            )

    def _validate_yolo_annotations(self):
        """
        Validates YOLO annotations in the dataset.

        This method checks the annotations in the directory, ensuring that each annotation file is valid.
        It also corrects issues based on the `fix_annotation` flag.

        Raises:
            ValueError: If the annotations directory does not exist or is missing.
        """
        annotations_dir = self.dataset.annotations_dir
        if not annotations_dir or not os.path.exists(annotations_dir):
            raise ValueError(
                f"Annotations directory is missing for dataset {self.dataset.name}."
            )

        for annotation_file in os.listdir(annotations_dir):
            if not annotation_file.endswith(".txt"):
                continue
            annotation_path = os.path.join(annotations_dir, annotation_file)
            with open(annotation_path) as file:
                lines = file.readlines()
            self._validate_annotation_file(lines=lines, annotation_file=annotation_file)

    def _validate_annotation_file(self, lines: list[str], annotation_file: str):
        """
        Validates an individual YOLO annotation file.

        This method processes each line in the annotation file, checking that all five fields (class ID,
        x_center, y_center, width, and height) are properly formatted and within valid bounds.

        Args:
            lines (List[str]): The lines from the annotation file to validate.
            annotation_file (str): The name of the annotation file.

        Raises:
            ValueError: If an annotation line is invalid.
        """
        for line_num, line in enumerate(lines, start=1):
            try:
                fields = list(map(float, line.strip().split()))
                if len(fields) != 5:
                    raise ValueError(
                        f"Line {line_num} in {annotation_file} does not have exactly 5 fields."
                    )

                class_id, x_center, y_center, width, height = fields
                self._validate_or_fix_annotation(
                    class_id=class_id,
                    x_center=x_center,
                    y_center=y_center,
                    width=width,
                    height=height,
                    line_num=line_num,
                    annotation_file=annotation_file,
                )
            except ValueError as e:
                raise ValueError(
                    f"Error in line {line_num} of {annotation_file}: {str(e)}"
                ) from e

    def _validate_or_fix_annotation(
        self,
        class_id: float,
        x_center: float,
        y_center: float,
        width: float,
        height: float,
        line_num: int,
        annotation_file: str,
    ):
        """
        Validates or fixes a single YOLO annotation.

        This method checks whether each annotation field (class ID, center coordinates, width, and height)
        is within the valid range. If an issue is found and `fix_annotation` is enabled, it corrects the value.

        Args:
            class_id (float): The class ID.
            x_center (float): The x center coordinate (normalized).
            y_center (float): The y center coordinate (normalized).
            width (float): The width (normalized).
            height (float): The height (normalized).
            line_num (int): The line number in the annotation file.
            annotation_file (str): The name of the annotation file.

        Returns:
            None: If the annotation is valid, or if fixed, the annotation file is updated.
        """
        class_id = self._validate_and_fix_class_id(class_id)
        x_center = self._validate_and_fix_coordinate(x_center, "x_center")
        y_center = self._validate_and_fix_coordinate(y_center, "y_center")
        width = self._validate_and_fix_size(width, "width")
        height = self._validate_and_fix_size(height, "height")

        if self.fix_annotation:
            new_line = f"{int(class_id)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
            self._update_annotation_file(
                annotation_file=annotation_file, line_num=line_num, new_line=new_line
            )

    def _validate_and_fix_class_id(self, class_id: float) -> float:
        """
        Validates and fixes the class ID if necessary.
        """
        if class_id < 0 or class_id >= len(self.dataset.labelmap):
            self.error_count["class_id"] += 1
            if self.fix_annotation:
                class_id = max(0, min(len(self.dataset.labelmap) - 1, int(class_id)))
        return class_id

    def _validate_and_fix_coordinate(
        self, coordinate: float, coordinate_name: str
    ) -> float:
        """
        Validates and fixes a coordinate (either x_center or y_center).
        """
        if not (0 <= coordinate <= 1):
            self.error_count[coordinate_name] += 1
            if self.fix_annotation:
                coordinate = max(0, min(1, coordinate))
        return coordinate

    def _validate_and_fix_size(self, size: float, size_name: str) -> float:
        """
        Validates and fixes a size (either width or height).
        """
        if not (0 < size <= 1):
            self.error_count[size_name] += 1
            if self.fix_annotation:
                size = max(0.01, min(1, size))
        return size

    def _update_annotation_file(
        self, annotation_file: str, line_num: int, new_line: str
    ):
        """
        Updates a specific line in the annotation file.

        This method replaces the old line with the corrected annotation line in the file.

        Args:
            annotation_file (str): The name of the annotation file to update.
            line_num (int): The line number to update.
            new_line (str): The updated line content.
        """
        if not self.dataset.annotations_dir:
            logger.info(
                f"Annotations directory is missing for dataset {self.dataset.name}, skipping update."
            )
            return
        annotation_path = os.path.join(self.dataset.annotations_dir, annotation_file)
        with open(annotation_path) as file:
            lines = file.readlines()
        lines[line_num - 1] = new_line
        with open(annotation_path, "w") as file:
            file.writelines(lines)

    def _report_errors(self):
        """
        Reports validation errors found in the dataset annotations.

        This method outputs a summary of the validation errors, including the number of issues found
        for each field (class ID, center coordinates, width, and height). If `fix_annotation` is enabled,
        the issues are automatically corrected.
        """
        logger.info(f"⚠️ Found {sum(self.error_count.values())} YOLO annotation issues:")
        for error_type, count in self.error_count.items():
            logger.info(f" - {error_type}: {count} issues")

        if self.fix_annotation:
            logger.info("🔧 Fixing these issues automatically...")
        else:
            raise ValueError(
                "YOLO annotation issues detected. Set 'fix_annotation' to True to automatically fix them."
            )
