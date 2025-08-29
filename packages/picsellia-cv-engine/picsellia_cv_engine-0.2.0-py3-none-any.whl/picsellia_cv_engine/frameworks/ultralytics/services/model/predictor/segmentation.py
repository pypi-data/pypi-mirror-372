import os

from ultralytics.engine.results import Results

from picsellia_cv_engine.core.data import (
    TBaseDataset,
)
from picsellia_cv_engine.core.models.picsellia_prediction import (
    PicselliaConfidence,
    PicselliaLabel,
    PicselliaPolygon,
    PicselliaPolygonPrediction,
)
from picsellia_cv_engine.core.services.model.predictor.model_predictor import (
    ModelPredictor,
)
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel


class UltralyticsSegmentationModelPredictor(ModelPredictor[UltralyticsModel]):
    """
    A predictor class that handles model inference and result post-processing for segmentation tasks
    using the Ultralytics framework.
    """

    def __init__(self, model: UltralyticsModel):
        """
        Initializes the segmentation predictor with the specified model.

        Args:
            model (UltralyticsModel): The model used to perform inference.
        """
        super().__init__(model)

    def run_inference_on_batches(self, image_batches: list[list[str]]) -> list[Results]:
        """
        Runs inference on each batch of images.

        Args:
            image_batches (list[list[str]]): A list of image path batches.

        Returns:
            list[Results]: The list of inference results for each batch.
        """
        return [self._run_inference(batch) for batch in image_batches]

    def _run_inference(self, batch_paths: list[str]) -> Results:
        """
        Executes model inference on a single batch of images.

        Args:
            batch_paths (list[str]): List of image paths.

        Returns:
            Results: The results of the inference for the batch.
        """
        return self.model.loaded_model(batch_paths)

    def post_process_batches(
        self,
        image_batches: list[list[str]],
        batch_results: list[Results],
        dataset: TBaseDataset,
    ) -> list[PicselliaPolygonPrediction]:
        """
        Converts raw predictions into PicselliaPolygonPrediction objects for each image.

        Args:
            image_batches (list[list[str]]): The original image path batches.
            batch_results (list[Results]): The inference results for each batch.
            dataset (TBaseDataset): Dataset used to retrieve asset metadata.

        Returns:
            list[PicselliaPolygonPrediction]: Structured predictions ready for evaluation/logging.
        """
        return [
            prediction
            for batch_paths, batch_result in zip(
                image_batches, batch_results, strict=False
            )
            for prediction in self._post_process(batch_paths, batch_result, dataset)
        ]

    def _post_process(
        self,
        image_paths: list[str],
        batch_prediction: Results,
        dataset: TBaseDataset,
    ) -> list[PicselliaPolygonPrediction]:
        """
        Processes a batch's prediction output and builds the final prediction objects.

        Args:
            image_paths (list[str]): Image paths for the current batch.
            batch_prediction (Results): Inference results for the batch.
            dataset (TBaseDataset): Dataset used to map predictions to assets and labels.

        Returns:
            list[PicselliaPolygonPrediction]: Processed predictions for each image.
        """
        processed_predictions = []

        for image_path, prediction in zip(image_paths, batch_prediction, strict=False):
            asset_id = os.path.basename(image_path).split(".")[0]
            asset = dataset.dataset_version.list_assets(ids=[asset_id])[0]

            polygons, labels, confidences = self.format_predictions(
                prediction=prediction, dataset=dataset
            )

            processed_predictions.append(
                PicselliaPolygonPrediction(
                    asset=asset,
                    polygons=polygons,
                    labels=labels,
                    confidences=confidences,
                )
            )

        return processed_predictions

    def format_predictions(
        self, prediction: Results, dataset: TBaseDataset
    ) -> tuple[list[PicselliaPolygon], list[PicselliaLabel], list[PicselliaConfidence]]:
        """
        Extracts and formats segmentation predictions into Picsellia types.

        Args:
            prediction (Results): A single inference result containing segmentation masks.
            dataset (TBaseDataset): Dataset used to resolve labels.

        Returns:
            tuple: Lists of PicselliaPolygon, PicselliaLabel, and PicselliaConfidence.
        """
        if prediction.masks is None:
            return [], [], []

        # Extract polygon segmentation masks
        polygons_list = [
            self.format_polygons(polygon) for polygon in prediction.masks.xy
        ]

        # Convert to Picsellia types
        picsellia_polygons = [PicselliaPolygon(points) for points in polygons_list]
        picsellia_labels = [
            self.get_picsellia_label(
                prediction.names[int(cls.cpu().numpy())],
                dataset=dataset,
            )
            for cls in prediction.boxes.cls
        ]
        picsellia_confidences = [
            PicselliaConfidence(float(conf.cpu().numpy()))
            for conf in prediction.boxes.conf
        ]

        return picsellia_polygons, picsellia_labels, picsellia_confidences

    @staticmethod
    def format_polygons(polygon) -> list[list[int]]:
        """
        Converts a polygon array to a list of integer coordinates.

        Args:
            polygon (np.ndarray): Polygon mask as an array of coordinates.

        Returns:
            list[list[int]]: Polygon represented as a list of integer point pairs.
        """
        return polygon.astype(int).tolist()
