from typing import Any

import numpy as np
from picsellia import Label, ModelVersion
from PIL.Image import Image
from sam2.build_sam import build_sam2
from sam2.modeling.sam2_base import SAM2Base
from sam2.sam2_image_predictor import SAM2ImagePredictor

from picsellia_cv_engine.core.models import Model
from picsellia_cv_engine.frameworks.sam2.services.predictor import SAM2ModelPredictor


class SAM2Model(Model):
    """
    SAM2 model wrapper for managing weight loading, mask generation, and runtime configuration.

    This class encapsulates the logic for working with SAM2 fine-tuning and inference
    within the Picsellia CV engine. It provides utilities to load a trained model from
    local files and attach a `SAM2AutomaticMaskGenerator` for downstream predictions.
    """

    def __init__(
        self,
        name: str,
        model_version: ModelVersion | None = None,
        pretrained_weights_name: str | None = None,
        trained_weights_name: str | None = None,
        config_name: str | None = None,
        exported_weights_name: str | None = None,
        labelmap: dict[str, Label] | None = None,
    ):
        """
        Initialize the SAM2 model wrapper.

        Args:
            name (str): Name of the model.
            model_version (ModelVersion): Associated Picsellia model version.
            pretrained_weights_name (str | None): Optional name of the pretrained weights file.
            trained_weights_name (str | None): Optional name of the fine-tuned weights file.
            config_name (str | None): Optional name of the SAM2 configuration file.
            exported_weights_name (str | None): Optional name for exported weights (e.g., ONNX).
            labelmap (dict[str, Label] | None): Optional label mapping for the dataset.
        """
        super().__init__(
            name=name,
            model_version=model_version,
            pretrained_weights_name=pretrained_weights_name,
            trained_weights_name=trained_weights_name,
            config_name=config_name,
            exported_weights_name=exported_weights_name,
            labelmap=labelmap,
        )
        self._loaded_predictor: Any | None = None

    @property
    def loaded_predictor(self) -> Any:
        """
        Return the loaded SAM2ImagePredictor instance.

        Returns:
            SAM2ImagePredictor: The initialized predictor for mask predictions.

        Raises:
            ValueError: If the generator has not been loaded yet.
        """
        if self._loaded_predictor is None:
            raise ValueError(
                "Predictor is not loaded. Please load the predictor before accessing it."
            )
        return self._loaded_predictor

    def set_loaded_predictor(self, predictor: Any) -> None:
        """
        Attach a loaded SAM2ImagePredictor instance to the model.

        Args:
            predictor (Any): The predictor instance to attach.
        """
        self._loaded_predictor = predictor

    def load_weights(
        self, weights_path: str, config_path: str, device: str
    ) -> tuple[SAM2Base, SAM2ImagePredictor]:
        """
        Load a SAM2 model and its mask generator from disk.

        Args:
            weights_path (str): Path to the model's trained checkpoint.
            config_path (str): Path to the model's YAML config file.
            device (str): Target device for inference, e.g., "cuda" or "cpu".

        Returns:
            tuple: A tuple of (SAM2 model, SAM2ImagePredictor).
        """
        model = build_sam2(config_path, weights_path, device=device)
        generator = SAM2ImagePredictor(sam_model=model)
        return model, generator

    def predict(
        self,
        image: Image,
        input_points: list[tuple[int, int]],
        input_labels: list[int],
        multimask_output: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Run prediction on an image with given input points and labels.

        Args:
            image (Image): The PIL image to segment.
            input_points (list[tuple[int, int]]): Coordinates of user-provided points.
            input_labels (list[int]): Labels for each point (1: foreground, 0: background).
            multimask_output (bool): Whether to return multiple mask hypotheses.

        Returns:
            list[dict]: Each dict contains:
                - "polygon": List of (x, y) coordinates
                - "score": IoU score associated with the mask
        """
        predictor = SAM2ModelPredictor(predictor=self.loaded_predictor)

        image_np = np.array(image)
        points_np = np.array(input_points)
        labels_np = np.array(input_labels)

        predictor.preprocess(image=image_np)

        masks_dict = predictor.run_inference(
            point_coords=points_np,
            point_labels=labels_np,
            multimask_output=multimask_output,
        )

        polygons_with_scores = predictor.post_process(results=masks_dict)
        return polygons_with_scores
