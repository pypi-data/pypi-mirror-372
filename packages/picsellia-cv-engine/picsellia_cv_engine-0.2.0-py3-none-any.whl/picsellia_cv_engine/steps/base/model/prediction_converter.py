import json
import logging
import os
from copy import deepcopy
from typing import Union

from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.models.picsellia_prediction import (
    PicselliaClassificationPrediction,
    PicselliaPolygonPrediction,
    PicselliaRectanglePrediction,
)
from picsellia_cv_engine.decorators.step_decorator import step

PredictionType = Union[
    PicselliaClassificationPrediction,
    PicselliaRectanglePrediction,
    PicselliaPolygonPrediction,
]

logger = logging.getLogger(__name__)


@step
def convert_predictions_to_coco(
    predictions: list[PredictionType],
    dataset: CocoDataset,
    use_id: bool = False,
) -> CocoDataset:
    """
    Convert a list of Picsellia predictions into COCO format annotations.

    Supports:
    - Classification (as single-class boxes covering full image)
    - Object detection (rectangle)
    - Segmentation (polygon)

    Args:
        predictions: List of predictions (classification, detection or segmentation)
        dataset: Dataset containing image + category info
        use_id: If True, match images using asset.id_with_extension instead of asset.filename

    Returns:
        Updated CocoDataset
    """

    coco = deepcopy(dataset.coco_data)
    coco["annotations"] = []

    image_name_to_id = {
        os.path.basename(image["file_name"]): image["id"] for image in coco["images"]
    }

    label_name_to_id = {cat["name"]: cat["id"] for cat in coco["categories"]}

    annotation_id = 0

    for prediction in predictions:
        image_name = (
            prediction.asset.id_with_extension if use_id else prediction.asset.filename
        )

        image_id = image_name_to_id.get(image_name)

        if image_id is None:
            logger.warning(f"Image not found in COCO dataset: {image_name}")
            continue

        if isinstance(prediction, PicselliaClassificationPrediction):
            category_id = label_name_to_id[prediction.label.name]
            coco["annotations"].append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "score": prediction.confidence.value,
                }
            )
            annotation_id += 1

        elif isinstance(prediction, PicselliaRectanglePrediction):
            for box, label, confidence in zip(
                prediction.boxes, prediction.labels, prediction.confidences
            ):
                category_id = label_name_to_id[label.name]
                coco["annotations"].append(
                    {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_id,
                        "bbox": [box.x, box.y, box.width, box.height],
                        "area": float(box.width * box.height),
                        "score": confidence.value,
                    }
                )
                annotation_id += 1

        elif isinstance(prediction, PicselliaPolygonPrediction):
            for polygon, label, confidence in zip(
                prediction.polygons, prediction.labels, prediction.confidences
            ):
                category_id = label_name_to_id[label.name]
                coco["annotations"].append(
                    {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_id,
                        "segmentation": [polygon.points],
                        "area": polygon.compute_area(),
                        "score": confidence.value,
                    }
                )
                annotation_id += 1

        else:
            logger.warning(f"Unsupported prediction type: {type(prediction)}")

    dataset.coco_data = coco
    with open(dataset.coco_file_path, "w") as f:
        json.dump(coco, f)

    logger.info(f"Converted {len(coco['annotations'])} annotations to COCO format.")
    return dataset
