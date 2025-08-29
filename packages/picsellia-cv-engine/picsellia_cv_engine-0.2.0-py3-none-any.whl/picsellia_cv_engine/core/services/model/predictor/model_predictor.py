import os
from abc import ABC
from typing import Generic, TypeVar

from picsellia_cv_engine.core import Model
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.models import (
    PicselliaConfidence,
    PicselliaLabel,
    PicselliaRectangle,
)

TModel = TypeVar("TModel", bound=Model)


class ModelPredictor(ABC, Generic[TModel]):
    """
    Abstract base class for model inference.

    Provides utility methods to standardize prediction outputs (labels, confidence, rectangles)
    into Picsellia-compatible structures.

    Attributes:
        model (TModel): The model instance used for inference.
    """

    def __init__(self, model: TModel):
        """
        Initialize the predictor with a loaded model.

        Args:
            model (TModel): The model context with loaded weights and configuration.

        Raises:
            ValueError: If the model does not have a loaded model instance.
        """
        self.model: TModel = model

        if not hasattr(self.model, "loaded_model"):
            raise ValueError("The models does not have a loaded models attribute.")

    def pre_process_dataset(self, dataset: TBaseDataset) -> list[str]:
        """
        Extracts all image paths from the dataset's image directory.

        Args:
            dataset (TBaseDataset): The dataset object containing the image directory.

        Returns:
            list[str]: A list of file paths to the dataset images.
        """
        if not dataset.images_dir:
            raise ValueError("No images directory found in the dataset.")

        return [
            os.path.join(dataset.images_dir, image_name)
            for image_name in os.listdir(dataset.images_dir)
        ]

    def prepare_batches(
        self, image_paths: list[str], batch_size: int
    ) -> list[list[str]]:
        return [
            image_paths[i : i + batch_size]
            for i in range(0, len(image_paths), batch_size)
        ]

    def get_picsellia_label(
        self, category_name: str, dataset: TBaseDataset
    ) -> PicselliaLabel:
        """
        Get or create a PicselliaLabel from a dataset category name.

        Args:
            category_name (str): The name of the label category.
            dataset (TBaseDataset): Dataset that provides label access.

        Returns:
            PicselliaLabel: Wrapped label object.
        """
        return PicselliaLabel(
            dataset.dataset_version.get_or_create_label(category_name)
        )

    def get_picsellia_confidence(self, confidence: float) -> PicselliaConfidence:
        """
        Wrap a confidence score in a PicselliaConfidence object.

        Args:
            confidence (float): Prediction confidence score.

        Returns:
            PicselliaConfidence: Wrapped confidence object.
        """
        return PicselliaConfidence(confidence)

    def get_picsellia_rectangle(
        self, x: int, y: int, w: int, h: int
    ) -> PicselliaRectangle:
        """
        Create a PicselliaRectangle from bounding box coordinates.

        Args:
            x (int): Top-left x-coordinate.
            y (int): Top-left y-coordinate.
            w (int): Width of the box.
            h (int): Height of the box.

        Returns:
            PicselliaRectangle: Rectangle wrapper for object detection.
        """
        return PicselliaRectangle(x=x, y=y, w=w, h=h)
