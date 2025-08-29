import logging
import os
import shutil

from ultralytics import YOLO

from picsellia_cv_engine.core.services.model.export.model_exporter import ModelExporter
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)

logger = logging.getLogger(__name__)


class UltralyticsModelExporter(ModelExporter):
    """
    Exporter class for Ultralytics models.

    This class handles the export process for models trained using the Ultralytics framework.
    It supports exporting to formats such as ONNX and relocating the exported model to a specified path.
    """

    def __init__(self, model: UltralyticsModel):
        """
        Initializes the UltralyticsModelExporter with a model instance.

        Args:
            model (UltralyticsModel): The model instance containing metadata and paths required for export.
        """
        super().__init__(model=model)
        self.model: UltralyticsModel = model

    def export_model(
        self,
        exported_model_destination_path: str,
        export_format: str,
        hyperparameters: UltralyticsHyperParameters,
    ) -> None:
        """
        Exports the model to the specified format and moves the file to a target directory.

        Args:
            exported_model_destination_path (str): Path to save the exported model.
            export_format (str): Export format (e.g., 'onnx').
            hyperparameters (UltralyticsHyperParameters): Export configuration including image size.

        Raises:
            ValueError: If the export directory or ONNX file cannot be found.
        """
        self._export_model(export_format=export_format, hyperparameters=hyperparameters)

        onnx_file_path = self._find_exported_onnx_file()

        self._move_onnx_to_destination_path(
            onnx_file_path=onnx_file_path,
            exported_model_destination_path=exported_model_destination_path,
        )

    def _export_model(
        self, export_format: str, hyperparameters: UltralyticsHyperParameters
    ) -> None:
        """
        Executes the export of the model using Ultralytics API.

        Args:
            export_format (str): Format to which the model should be exported.
            hyperparameters (UltralyticsHyperParameters): Contains export settings such as image size.
        """
        loaded_model: YOLO = self.model.loaded_model
        loaded_model.export(
            format=export_format,
            imgsz=hyperparameters.image_size,
            dynamic=False,
            batch=1,
            opset=18,  # ONNX opset version compatible with IR 8
        )

    def _find_exported_onnx_file(self) -> str:
        """
        Locates the exported ONNX file in the model's weights directory.

        Returns:
            str: Absolute path to the ONNX file.

        Raises:
            ValueError: If no ONNX file is found in the expected directory.
        """
        if not self.model.latest_run_dir:
            raise ValueError("The latest run directory is not set.")
        ultralytics_weights_dir = os.path.join(self.model.latest_run_dir, "weights")
        onnx_files = [
            f for f in os.listdir(ultralytics_weights_dir) if f.endswith(".onnx")
        ]
        if not onnx_files:
            raise ValueError("No ONNX file found")
        return os.path.join(ultralytics_weights_dir, onnx_files[0])

    def _move_onnx_to_destination_path(
        self, onnx_file_path: str, exported_model_destination_path: str
    ) -> None:
        """
        Moves the exported ONNX model to the destination directory.

        If a file with the same name exists, it will be overwritten.

        Args:
            onnx_file_path (str): Path to the ONNX file.
            exported_model_destination_path (str): Target directory where the file will be moved.
        """
        logger.info(f"Moving ONNX file to {exported_model_destination_path}...")

        if os.path.exists(
            os.path.join(
                exported_model_destination_path, os.path.basename(onnx_file_path)
            )
        ):
            logger.warning(
                f"File already exists at destination. Removing: {os.path.join(exported_model_destination_path, os.path.basename(onnx_file_path))}"
            )
            os.remove(
                os.path.join(
                    exported_model_destination_path, os.path.basename(onnx_file_path)
                )
            )

        shutil.move(onnx_file_path, exported_model_destination_path)
        logger.info("Move completed successfully.")
