import logging
import os
import re
from abc import abstractmethod
from pathlib import Path
from typing import Any

from picsellia import Experiment, ModelFile, ModelVersion

from picsellia_cv_engine.core import Model

logger = logging.getLogger("picsellia-engine")


class ModelExporter:
    """
    Base class for exporting and saving a model.

    This class provides a standard interface for exporting models and saving them
    to a Picsellia experiment or model version.
    """

    def __init__(self, model: Model):
        """
        Initialize the exporter with a model instance.

        Args:
            model (Model): The model to export.
        """
        self.model = model

    @abstractmethod
    def export_model(
        self,
        exported_model_destination_path: str,
        export_format: str,
        hyperparameters: Any,
    ):
        """
        Abstract method to export the model.

        Must be implemented in subclasses.

        Args:
            exported_model_destination_path (str): Directory to export the model to.
            export_format (str): Format to export the model in.
            hyperparameters (Any): Optional export configuration.
        """
        pass

    def save_model_to_experiment(
        self,
        experiment: Experiment,
        exported_weights_path: str,
        exported_weights_name: str,
    ) -> None:
        """
        Save exported model to a Picsellia experiment.

        Args:
            experiment (Experiment): Target experiment.
            exported_weights_path (str): Path to exported weights directory.
            exported_weights_name (str): File name to use in Picsellia.
        """
        self._store_artifact(
            target=experiment,
            exported_weights_path=exported_weights_path,
            exported_weights_name=exported_weights_name,
        )

    def save_model_to_model_version(
        self,
        model_version: ModelVersion,
        exported_weights_path: str,
        exported_weights_name: str,
    ) -> None:
        """
        Save exported model to a Picsellia model version.

        Args:
            model_version (ModelVersion): Target model version.
            exported_weights_path (str): Path to exported weights directory.
            exported_weights_name (str): File name to use in Picsellia.
        """
        self._store_artifact(
            target=model_version,
            exported_weights_path=exported_weights_path,
            exported_weights_name=exported_weights_name,
        )

    def _get_unique_file_name(
        self, exported_weights_name: str, target_files: list[ModelFile]
    ) -> str:
        """
        Generate a unique name for the model file if a name conflict exists.

        Args:
            exported_weights_name (str): Desired name of the file.
            target_files (list[ModelFile]): Existing files in the target.

        Returns:
            str: A unique file name.
        """
        unique_name = self._sanitize_filename(filename=exported_weights_name)
        existing_files = [file.name for file in target_files]

        if unique_name in existing_files:
            i = 2

            while f"{unique_name}_{i}" in existing_files:
                i += 1

            unique_name = f"{unique_name}_{i}"
            logger.warning(
                f"⚠️ Model with name {exported_weights_name} already exists in the target. Renaming to {unique_name}"
            )

        return unique_name

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename to comply with Picsellia constraints.

        Replaces invalid characters with underscores and removes redundancy.

        Args:
            filename (str): Filename to sanitize.

        Returns:
            str: Sanitized filename.
        """
        # Replace spaces and invalid chars with underscore
        sanitized = re.sub(r"[^a-zA-Z0-9-]", "_", filename)

        # Remove multiple consecutive underscores
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")
        return sanitized

    def _store_artifact(
        self,
        target: Experiment | ModelVersion,
        exported_weights_path: str,
        exported_weights_name: str,
    ) -> None:
        """
        Store model weights to an experiment or model version.

        If multiple files are found in the directory, they will be zipped.

        Args:
            target (Experiment | ModelVersion): Destination for the model.
            exported_weights_path (str): Path to the export folder.
            exported_weights_name (str): Name under which to save the model.

        Raises:
            ValueError: If export path is invalid or empty.
        """
        weights_dir = Path(exported_weights_path)
        if not weights_dir.exists():
            raise ValueError(f"Export directory does not exist: {weights_dir}")

        exported_files = list(weights_dir.iterdir())
        if not exported_files:
            raise ValueError(f"No models files found in: {weights_dir}")

        if isinstance(target, ModelVersion):
            exported_weights_name = self._get_unique_file_name(
                exported_weights_name, target.list_files()
            )

        if len(exported_files) > 1:
            target.store(
                name=exported_weights_name,
                path=exported_weights_path,
                do_zip=True,
            )
        else:
            target.store(
                name=exported_weights_name,
                path=os.path.join(
                    exported_weights_path,
                    exported_files[0],
                ),
            )
