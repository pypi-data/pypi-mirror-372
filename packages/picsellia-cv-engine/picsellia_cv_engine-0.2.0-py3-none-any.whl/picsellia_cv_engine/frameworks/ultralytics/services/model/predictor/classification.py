import os

from ultralytics.engine.results import Results

from picsellia_cv_engine.core.data import (
    TBaseDataset,
)
from picsellia_cv_engine.core.models import PicselliaClassificationPrediction
from picsellia_cv_engine.core.services.model.predictor.model_predictor import (
    ModelPredictor,
)
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel


class UltralyticsClassificationModelPredictor(ModelPredictor[UltralyticsModel]):
    """
    A predictor class that handles model inference and result post-processing for classification tasks
    using the Ultralytics framework.

    This class performs pre-processing of datasets, runs inference on batches of images, and post-processes
    the predictions to generate PicselliaClassificationPrediction objects for classification tasks.
    """

    def __init__(self, model: UltralyticsModel):
        """
        Initializes the UltralyticsClassificationModelPredictor with a provided model.

        Args:
            model (UltralyticsModel): The context containing the loaded model and its configurations.
        """
        super().__init__(model)

    def pre_process_dataset(self, dataset: TBaseDataset) -> list[str]:
        """
        Prepares the dataset by extracting and returning a list of image file paths from the dataset directory.

        Args:
            dataset (TBaseDataset): The dataset containing image directories structured by class.

        Returns:
            list[str]: A list of full image file paths.
        """
        if not dataset.images_dir:
            raise ValueError("No images directory found in the dataset.")
        image_paths = []
        for category_name in os.listdir(dataset.images_dir):
            category_dir = os.path.join(dataset.images_dir, category_name)
            image_paths.extend(
                [
                    os.path.join(category_dir, image_name)
                    for image_name in os.listdir(category_dir)
                ]
            )
        return image_paths

    def run_inference_on_batches(self, image_batches: list[list[str]]) -> list[Results]:
        """
        Runs inference on each batch of images using the model.

        Args:
            image_batches (list[list[str]]): Batches of image paths.

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
        Executes inference on a single batch using the loaded Ultralytics model.

        Args:
            batch_paths (list[str]): A batch of image paths.

        Returns:
            Results: Inference result for the given batch.
        """
        return self.model.loaded_model(batch_paths)

    def post_process_batches(
        self,
        image_batches: list[list[str]],
        batch_results: list[Results],
        dataset: TBaseDataset,
    ) -> list[PicselliaClassificationPrediction]:
        """
        Post-processes all inference results by matching predictions with assets.

        Args:
            image_batches (list[list[str]]): List of image batches.
            batch_results (list[Results]): Corresponding model outputs for each batch.
            dataset (TBaseDataset): Dataset used to resolve label references.

        Returns:
            list[PicselliaClassificationPrediction]: Formatted predictions.
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
    ) -> list[PicselliaClassificationPrediction]:
        """
        Converts raw model outputs into Picsellia-compatible classification predictions.

        Args:
            image_paths (list[str]): List of image paths corresponding to predictions.
            batch_prediction (Results): Raw model output for the batch.
            dataset (TBaseDataset): Dataset used for asset resolution and label lookup.

        Returns:
            list[PicselliaClassificationPrediction]: Final structured predictions.
        """
        processed_predictions = []

        for image_path, prediction in zip(image_paths, batch_prediction, strict=False):
            asset_id = os.path.basename(image_path).split(".")[0]
            asset = dataset.dataset_version.list_assets(ids=[asset_id])[0]
            predicted_label = self.get_picsellia_label(
                prediction.names[int(prediction.probs.top1)], dataset
            )
            prediction_confidence = self.get_picsellia_confidence(
                float(prediction.probs.top1conf.cpu().numpy())
            )
            processed_prediction = PicselliaClassificationPrediction(
                asset=asset,
                label=predicted_label,
                confidence=prediction_confidence,
            )
            processed_predictions.append(processed_prediction)

        return processed_predictions
