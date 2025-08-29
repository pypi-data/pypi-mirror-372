import logging
import os

import torch
from picsellia import Label, ModelVersion
from ultralytics import YOLO

from picsellia_cv_engine.core.models import Model

logger = logging.getLogger(__name__)


def find_latest_run_dir(dir: str, model_name: str) -> str:
    """
    Finds the latest run directory for a given model name.

    This function looks for subdirectories starting with the model name and returns
    the most recent one (by sorting the folder names ending with digits).

    Args:
        dir (str): Path to the directory containing run folders.
        model_name (str): Prefix used to identify run folders.

    Returns:
        str: Path to the most recent run directory.

    Raises:
        ValueError: If no matching run directory is found.
    """
    run_dirs = os.listdir(dir)
    run_dirs = [f for f in run_dirs if f.startswith(model_name)]
    if not run_dirs:
        raise ValueError("No results folder found")
    elif len(run_dirs) == 1:
        return os.path.join(dir, run_dirs[0])

    return os.path.join(
        dir,
        sorted([f for f in run_dirs if f[-1].isdigit()])[-1],
    )


class UltralyticsModel(Model):
    """
    Specialized model class for handling Ultralytics models.

    This class extends the base `Model` class to support Ultralytics-specific logic
    such as automatically locating the latest run directory and setting the trained weights' path.
    """

    def __init__(
        self,
        name: str,
        model_version: ModelVersion,
        pretrained_weights_name: str | None = None,
        trained_weights_name: str | None = None,
        config_name: str | None = None,
        exported_weights_name: str | None = None,
        labelmap: dict[str, Label] | None = None,
    ):
        """
        Initializes the UltralyticsModel.

        Args:
            name (str): Name of the model.
            model_version (ModelVersion): Picsellia ModelVersion associated with the model.
            pretrained_weights_name (Optional[str]): Name of the pretrained weights file.
            trained_weights_name (Optional[str]): Name of the trained weights file.
            config_name (Optional[str]): Name of the config file.
            exported_weights_name (Optional[str]): Name of the exported weights file.
            labelmap (Optional[dict[str, Label]]): Label map for the model.
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
        self.latest_run_dir: str | None = None

    def load_yolo_weights(self, weights_path: str, device: str) -> YOLO:
        """
        Loads a YOLO model from the given weights file and moves it to the specified device.

        This function loads a YOLO model using the provided weights path and transfers it
        to the specified device (e.g., 'cpu' or 'cuda'). It raises an error if the weights
        file is not found or cannot be loaded.

        Args:
            weights_path (str): The file path to the YOLO model weights.
            device (str): The device to which the model should be moved ('cpu' or 'cuda').

        Returns:
            YOLO: The loaded YOLO model ready for inference or training.

        Raises:
            RuntimeError: If the weights file cannot be loaded or the device is unavailable.
        """
        loaded_model = YOLO(weights_path)
        torch_device = torch.device(device)
        logger.info(f"Loading model on device: {torch_device}")
        loaded_model.to(device=device)
        return loaded_model

    def set_latest_run_dir(self):
        """
        Sets the path to the latest run directory.

        Uses the results directory to find and assign the most recent run folder.
        Raises an error if the results directory is not set or does not exist.
        """
        if not self.results_dir or not os.path.exists(self.results_dir):
            raise ValueError("The results directory is not set.")
        self.latest_run_dir = find_latest_run_dir(self.results_dir, self.name)

    def set_trained_weights_path(self):
        """
        Sets the path to the trained weights file from the latest run directory.

        Assumes the file is stored as `best.pt` inside a `weights/` subdirectory.
        Raises an error if the required directories do not exist.
        """
        if not self.results_dir or not os.path.exists(self.results_dir):
            raise ValueError("The results directory is not set.")
        if not self.latest_run_dir or not os.path.exists(self.latest_run_dir):
            raise ValueError("The latest run directory is not set.")
        trained_weights_dir = os.path.join(self.latest_run_dir, "weights")
        self.trained_weights_path = os.path.join(trained_weights_dir, "best.pt")
