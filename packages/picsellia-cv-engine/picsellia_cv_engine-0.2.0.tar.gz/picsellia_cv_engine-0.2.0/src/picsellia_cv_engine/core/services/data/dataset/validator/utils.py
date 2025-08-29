import logging
from typing import Any

from picsellia.types.enums import InferenceType

from picsellia_cv_engine.core.data import (
    CocoDataset,
    TBaseDataset,
    YoloDataset,
)
from picsellia_cv_engine.core.services.data.dataset.validator.classification.coco_classification_dataset_context_validator import (
    CocoClassificationDatasetValidator,
)
from picsellia_cv_engine.core.services.data.dataset.validator.common import (
    DatasetValidator,
)
from picsellia_cv_engine.core.services.data.dataset.validator.object_detection.coco_object_detection_dataset_validator import (
    CocoObjectDetectionDatasetValidator,
)
from picsellia_cv_engine.core.services.data.dataset.validator.object_detection.yolo_object_detection_dataset_validator import (
    YoloObjectDetectionDatasetValidator,
)
from picsellia_cv_engine.core.services.data.dataset.validator.segmentation.coco_segmentation_dataset_validator import (
    CocoSegmentationDatasetValidator,
)
from picsellia_cv_engine.core.services.data.dataset.validator.segmentation.yolo_segmentation_dataset_validator import (
    YoloSegmentationDatasetValidator,
)

logger = logging.getLogger(__name__)


def get_dataset_validator(dataset: TBaseDataset, fix_annotation: bool = True) -> Any:
    """Retrieves the appropriate validator for a given dataset.

    Args:
        dataset (TBaseDataset): The dataset to validate.
        fix_annotation (bool, optional): A flag to indicate whether to automatically fix errors (default is True).

    Returns:
        Any: The validator instance or None if the dataset type is unsupported.
    """
    validators = {
        (
            CocoDataset,
            InferenceType.CLASSIFICATION,
        ): CocoClassificationDatasetValidator,
        (
            CocoDataset,
            InferenceType.OBJECT_DETECTION,
        ): CocoObjectDetectionDatasetValidator,
        (
            CocoDataset,
            InferenceType.SEGMENTATION,
        ): CocoSegmentationDatasetValidator,
        (
            YoloDataset,
            InferenceType.OBJECT_DETECTION,
        ): YoloObjectDetectionDatasetValidator,
        (
            YoloDataset,
            InferenceType.SEGMENTATION,
        ): YoloSegmentationDatasetValidator,
    }

    inference_type = dataset.dataset_version.type

    if inference_type == InferenceType.NOT_CONFIGURED:
        return DatasetValidator(dataset=dataset)

    validator_class = validators.get((type(dataset), inference_type))

    if validator_class is None:
        logger.warning(
            f"Dataset type '{type(dataset).__name__}' with inference type '{inference_type.name}' is not supported. Skipping validation."
        )
        return None

    return validator_class(dataset=dataset, fix_annotation=fix_annotation)
