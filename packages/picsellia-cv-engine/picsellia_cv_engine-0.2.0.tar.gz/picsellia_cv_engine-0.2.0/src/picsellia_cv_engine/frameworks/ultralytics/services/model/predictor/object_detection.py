import os

from picsellia import Asset
from ultralytics.engine.results import Results

from picsellia_cv_engine.core.data import (
    TBaseDataset,
)
from picsellia_cv_engine.core.models.picsellia_prediction import (
    PicselliaConfidence,
    PicselliaLabel,
    PicselliaRectangle,
    PicselliaRectanglePrediction,
)
from picsellia_cv_engine.core.services.model.predictor.model_predictor import (
    ModelPredictor,
)
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel


class UltralyticsDetectionModelPredictor(ModelPredictor[UltralyticsModel]):
    """
    A predictor class that handles inference and result formatting for object detection tasks
    using the Ultralytics framework.
    """

    def __init__(self, model: UltralyticsModel):
        """
        Initializes the UltralyticsDetectionModelPredictor with the specified model.

        Args:
            model (UltralyticsModel): The detection model with its weights and configuration loaded.
        """
        super().__init__(model)

    def run_inference_on_batches(self, image_batches: list[list[str]]) -> list[Results]:
        """
        Runs inference on each image batch using the model.

        Args:
            image_batches (list[list[str]]): A list of image batches.

        Returns:
            list[Results]: A list of inference result objects, one per batch.
        """
        all_batch_results = []

        for batch_paths in image_batches:
            batch_results = self._run_inference(batch_paths)
            all_batch_results.append(batch_results)
        return all_batch_results

    def _run_inference(self, batch_paths: list[str]) -> Results:
        """
        Runs inference on a single batch of image paths.

        Args:
            batch_paths (list[str]): List of paths for the current batch.

        Returns:
            Results: The Ultralytics model's inference result.
        """
        return self.model.loaded_model(batch_paths)

    def post_process_batches(
        self,
        image_batches: list[list[str]],
        batch_results: list[Results],
        dataset: TBaseDataset,
    ) -> list[PicselliaRectanglePrediction]:
        """
        Converts raw model outputs into structured rectangle predictions.

        Args:
            image_batches (list[list[str]]): List of image batches.
            batch_results (list[Results]): Model predictions per batch.
            dataset (TBaseDataset): Dataset context used for label resolution.

        Returns:
            list[PicselliaRectanglePrediction]: Structured prediction results per image.
        """
        all_predictions = []

        for batch_result, batch_paths in zip(
            batch_results, image_batches, strict=False
        ):
            all_predictions.extend(
                self._post_process(
                    image_paths=batch_paths,
                    batch_prediction=batch_result,
                    dataset=dataset,
                )
            )
        return all_predictions

    def _post_process(
        self,
        image_paths: list[str],
        batch_prediction: Results,
        dataset: TBaseDataset,
    ) -> list[PicselliaRectanglePrediction]:
        """
        Converts prediction results for a batch into PicselliaRectanglePrediction objects.

        Args:
            image_paths (list[str]): The image paths corresponding to the predictions.
            batch_prediction (Results): The raw prediction results.
            dataset (TBaseDataset): Dataset used for label matching.

        Returns:
            list[PicselliaRectanglePrediction]: Formatted detection predictions.
        """
        processed_predictions = []

        for image_path, prediction in zip(image_paths, batch_prediction, strict=False):
            asset_id = os.path.basename(image_path).split(".")[0]
            asset = dataset.dataset_version.list_assets(ids=[asset_id])[0]

            boxes, labels, confidences = self.format_predictions(
                asset=asset, prediction=prediction, dataset=dataset
            )

            processed_prediction = PicselliaRectanglePrediction(
                asset=asset,
                boxes=boxes,
                labels=labels,
                confidences=confidences,
            )
            processed_predictions.append(processed_prediction)

        return processed_predictions

    def format_predictions(
        self, asset: Asset, prediction: Results, dataset: TBaseDataset
    ) -> tuple[
        list[PicselliaRectangle], list[PicselliaLabel], list[PicselliaConfidence]
    ]:
        """
        Transforms raw model predictions into Picsellia-compatible rectangle, label, and confidence objects.

        Args:
            asset (Asset): The asset corresponding to the image.
            prediction (Results): The prediction results for the image.
            dataset (TBaseDataset): The dataset used to retrieve label mappings.

        Returns:
            tuple: Lists of PicselliaRectangle, PicselliaLabel, and PicselliaConfidence objects.
        """
        if not prediction.boxes:
            return [], [], []

        # Extract normalized boxes and rescale them
        normalized_boxes = prediction.boxes.xyxyn.cpu().numpy()
        boxes_list = [
            self.rescale_normalized_box(box, asset.width, asset.height)
            for box in normalized_boxes
        ]
        casted_boxes = [self.cast_type_list_to_int(box) for box in boxes_list]

        # Convert to Picsellia types
        picsellia_boxes = [PicselliaRectangle(*box) for box in casted_boxes]
        picsellia_labels = [
            self.get_picsellia_label(prediction.names[int(cls.cpu().numpy())], dataset)
            for cls in prediction.boxes.cls
        ]
        picsellia_confidences = [
            PicselliaConfidence(float(conf.cpu().numpy()))
            for conf in prediction.boxes.conf
        ]

        return picsellia_boxes, picsellia_labels, picsellia_confidences

    @staticmethod
    def rescale_normalized_box(box, width, height) -> list[int]:
        """
        Rescales a bounding box from normalized coordinates to pixel dimensions.

        Args:
            box (list): Normalized box in [x_min, y_min, x_max, y_max] format.
            width (int): Image width.
            height (int): Image height.

        Returns:
            list[int]: Rescaled box in [x, y, width, height] format.
        """
        x_min, y_min, x_max, y_max = box
        return [
            int(x_min * width),
            int(y_min * height),
            int((x_max - x_min) * width),
            int((y_max - y_min) * height),
        ]

    @staticmethod
    def cast_type_list_to_int(box) -> list[int]:
        """
        Converts all values in a box list to integers.

        Args:
            box (list[float]): Bounding box coordinates.

        Returns:
            list[int]: Bounding box with integer values.
        """
        return [int(value) for value in box]
