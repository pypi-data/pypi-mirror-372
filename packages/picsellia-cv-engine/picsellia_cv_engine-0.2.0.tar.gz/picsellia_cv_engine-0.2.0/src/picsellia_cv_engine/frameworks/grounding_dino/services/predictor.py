import os

import cv2

from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.models.picsellia_prediction import (
    PicselliaConfidence,
    PicselliaRectangle,
    PicselliaRectanglePrediction,
)
from picsellia_cv_engine.core.services.model.predictor.model_predictor import (
    ModelPredictor,
)
from picsellia_cv_engine.frameworks.grounding_dino.model.model import GroundingDinoModel


class GroundingDinoDetectionModelPredictor(ModelPredictor):
    """
    A predictor class to run GroundingDINO inference for object detection.
    Converts results into PicselliaRectanglePrediction objects.
    """

    def __init__(
        self,
        model: GroundingDinoModel,
        label_names: list[str],
        box_threshold: float = 0.5,
        text_threshold: float = 0.5,
    ):
        """
        Initialize the predictor.

        Args:
            model (GroundingDinoModel): Loaded GroundingDINO model.
            label_names (list[str]): list of class names to detect.
        """
        super().__init__(model=model)
        self.model = model
        self.label_names = label_names
        self.box_threshold = box_threshold
        self.text_threshold = text_threshold

    def run_inference_on_batches(
        self, image_batches: list[list[str]]
    ) -> list[list[dict]]:
        all_batch_results = []

        for batch in image_batches:
            batch_predictions = []
            for image_path in batch:
                prediction = self._run_inference(image_path)
                batch_predictions.append(prediction)
            all_batch_results.append(batch_predictions)

        return all_batch_results

    def _run_inference(self, image_path: str) -> dict:
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")

        detections = self.model.loaded_model.predict_with_classes(
            image=image_bgr,
            classes=self.label_names,
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold,
        )

        return {
            "boxes": detections.xyxy,
            "classes": detections.class_id,
            "confidences": detections.confidence,
            "width": image_bgr.shape[1],
            "height": image_bgr.shape[0],
        }

    def post_process_batches(
        self,
        image_batches: list[list[str]],
        batch_results: list[list[dict]],
        dataset: TBaseDataset,
    ) -> list[PicselliaRectanglePrediction]:
        all_predictions = []

        for batch_paths, batch_results_per_image in zip(image_batches, batch_results):
            for image_path, prediction_data in zip(
                batch_paths, batch_results_per_image
            ):
                if not prediction_data or any(
                    prediction_data.get(k) is None
                    for k in ["boxes", "classes", "confidences"]
                ):
                    continue

                processed = self._post_process(
                    image_path=image_path,
                    prediction=prediction_data,
                    dataset=dataset,
                )
                if processed:
                    all_predictions.append(processed)

        return all_predictions

    def _post_process(
        self,
        image_path: str,
        prediction: dict,
        dataset: TBaseDataset,
    ) -> PicselliaRectanglePrediction | None:
        asset_id = os.path.basename(image_path).split(".")[0]
        asset = dataset.dataset_version.list_assets(ids=[asset_id])[0]

        if not prediction["boxes"]:
            return None

        boxes, labels, confidences = [], [], []

        for i, box in enumerate(prediction["boxes"]):
            try:
                x_min, y_min, x_max, y_max = box
                w, h = x_max - x_min, y_max - y_min
                boxes.append(PicselliaRectangle(int(x_min), int(y_min), int(w), int(h)))

                label_idx = int(prediction["classes"][i])
                label = self.get_picsellia_label(self.label_names[label_idx], dataset)
                labels.append(label)

                confidence = float(prediction["confidences"][i])
                confidences.append(PicselliaConfidence(confidence))

            except (ValueError, TypeError, IndexError):
                continue

        if not boxes:
            return None

        return PicselliaRectanglePrediction(
            asset=asset,
            boxes=boxes,
            labels=labels,
            confidences=confidences,
        )
