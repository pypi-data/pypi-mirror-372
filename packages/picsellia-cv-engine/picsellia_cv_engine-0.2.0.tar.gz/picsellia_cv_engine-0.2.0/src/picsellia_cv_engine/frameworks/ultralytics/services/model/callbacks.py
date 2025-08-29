import logging
import os
from pathlib import Path
from typing import Callable, TypeVar

from picsellia import Experiment
from ultralytics.engine.trainer import BaseTrainer
from ultralytics.engine.validator import BaseValidator

from picsellia_cv_engine.core.services.model.logging import (
    BaseLogger,
    MetricMapping,
)
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel

logger = logging.getLogger(__name__)

TBaseLogger = TypeVar("TBaseLogger", bound=BaseLogger)
TMetricMapping = TypeVar("TMetricMapping", bound=MetricMapping)
TBaseTrainer = TypeVar("TBaseTrainer", bound=BaseTrainer)
TBaseValidator = TypeVar("TBaseValidator", bound=BaseValidator)


class UltralyticsCallbacks:
    """
    Provides callback hooks for training and evaluation lifecycle events in Ultralytics YOLO models.

    This class integrates with Picsellia to log metrics, images, and artifacts
    during the training and validation process.
    """

    def __init__(
        self,
        experiment: Experiment,
        logger: type[TBaseLogger],
        metric_mapping: TMetricMapping,
        model: UltralyticsModel,
        save_period: int,
    ):
        """
        Initializes the UltralyticsCallbacks.

        Args:
            experiment (Experiment): The experiment object used for logging.
            logger (type[TBaseLogger]): The logger class used for metric/image logging.
            metric_mapping (TMetricMapping): Maps framework-specific metric names to standard names.
            model (UltralyticsModel): The model wrapper to manage artifacts and paths.
            save_period (int): Frequency (in epochs) to save model checkpoints.
        """
        self.logger = logger(experiment=experiment, metric_mapping=metric_mapping)
        self.experiment = experiment
        self.model = model
        self.save_period = save_period

    def on_train_epoch_end(self, trainer: TBaseTrainer):
        """
        Callback called at the end of each training epoch.
        Logs training and validation losses, learning rates, and periodically saves the model.

        Args:
            trainer (TBaseTrainer): The trainer object with training state and losses.
        """
        for metric_name, loss_value in trainer.label_loss_items(trainer.tloss).items():
            if metric_name.startswith("val") or metric_name.startswith("metrics"):
                self.logger.log_metric(
                    name=metric_name, value=float(loss_value), phase="val"
                )
            else:
                self.logger.log_metric(
                    name=metric_name, value=float(loss_value), phase="train"
                )

        for lr_name, lr_value in trainer.lr.items():
            self.logger.log_metric(name=lr_name, value=float(lr_value), phase="train")

        if (trainer.epoch + 1) % self.save_period == 0 and trainer.epoch != 0:
            self._save_checkpoint_to_experiment(epoch=trainer.epoch + 1)

    def on_fit_epoch_end(self, trainer: TBaseTrainer):
        """
        Callback called at the end of each epoch (after validation).
        Logs time, metrics, and training images.

        Args:
            trainer (TBaseTrainer): The trainer object with metrics and epoch info.
        """
        self.logger.log_metric(
            name="epoch_time", value=float(trainer.epoch_time), phase="train"
        )

        for metric_name, metric_value in trainer.metrics.items():
            if metric_name.startswith("val") or metric_name.startswith("metrics"):
                self.logger.log_metric(
                    name=metric_name, value=float(metric_value), phase="val"
                )
            else:
                self.logger.log_metric(
                    name=metric_name, value=float(metric_value), phase="train"
                )

        if trainer.epoch == 0:
            from ultralytics.utils.torch_utils import model_info_for_loggers

            for info_key, info_value in model_info_for_loggers(trainer).items():
                if info_key == "model/parameters":
                    continue
                self.logger.log_value(name=info_key, value=info_value)

        train_output_directory = Path(trainer.save_dir)
        valid_prefixes = ("train", "labels")
        files = [
            file
            for file in train_output_directory.iterdir()
            if file.stem.startswith(valid_prefixes)
        ]
        existing_files: list[Path] = [
            train_output_directory / file_name for file_name in files
        ]
        for file_path in existing_files:
            self.logger.log_image(
                name=file_path.stem, image_path=str(file_path), phase="train"
            )

    def on_val_end(self, validator: TBaseValidator):
        """
        Callback called after validation.
        Logs validation result images and performance metrics.

        Args:
            validator (TBaseValidator): The validator object with validation metrics.
        """
        val_output_directory = Path(validator.save_dir)

        valid_prefixes = ("val", "P", "R", "F1", "Box", "Mask")
        files = [
            file
            for file in val_output_directory.iterdir()
            if file.stem.startswith(valid_prefixes)
        ]
        existing_files: list[Path] = [
            val_output_directory / file_name for file_name in files
        ]
        for file_path in existing_files:
            self.logger.log_image(
                name=file_path.stem, image_path=str(file_path), phase="val"
            )

        desc = validator.get_desc()
        column_names = extract_column_names(desc)

        if hasattr(validator, "metrics") and hasattr(
            validator.metrics, "ap_class_index"
        ):
            table_data = []
            row_labels = []

            for i, c in enumerate(validator.metrics.ap_class_index):
                class_name = validator.names[c]
                row_labels.append(class_name)

                row = [
                    int(validator.nt_per_image[c]),
                    int(validator.nt_per_class[c]),
                ]

                metrics = validator.metrics.class_result(i)
                row += [round(m, 3) for m in metrics]

                table_data.append(row)

            columns = column_names[
                1:
            ]  # Skip 'Class', because we use row_labels instead

            self.logger.log_table(
                name="metrics",
                data={
                    "data": table_data,
                    "rows": row_labels,
                    "columns": columns,
                },
                phase="val",
            )

        elif hasattr(validator, "metrics") and hasattr(
            validator.metrics, "top1"
        ):  # Classification
            self.logger.log_table(
                name="metrics",
                data={
                    "columns": ["top1_acc", "top5_acc"],
                    "rows": ["all"],
                    "data": [
                        [
                            round(validator.metrics.top1, 3),
                            round(validator.metrics.top5, 3),
                        ]
                    ],
                },
                phase="val",
            )

    def on_train_end(self, trainer: TBaseTrainer):
        """
        Callback called at the end of training.
        Currently logs final metrics (disabled by default).

        Args:
            trainer (TBaseTrainer): The trainer object.
        """
        # Reserved for future use or manual reactivation for metrics logging

    def get_callbacks(self) -> dict[str, Callable]:
        """
        Returns the dictionary of callback methods for integration into the Ultralytics engine.

        Returns:
            dict: Callback function names mapped to their handlers.
        """
        return {
            "on_train_epoch_end": self.on_train_epoch_end,
            "on_fit_epoch_end": self.on_fit_epoch_end,
            "on_val_end": self.on_val_end,
            "on_train_end": self.on_train_end,
        }

    def _save_checkpoint_to_experiment(self, epoch: int):
        """
        Saves the trained model weights to the experiment as an artifact.

        Args:
            epoch (int): The epoch number associated with the checkpoint.
        """
        self.model.set_latest_run_dir()
        self.model.set_trained_weights_path()
        best_weights_path = self.model.trained_weights_path

        if best_weights_path and os.path.exists(best_weights_path):
            self.model.save_artifact_to_experiment(
                experiment=self.experiment,
                artifact_name="best-model",
                artifact_path=best_weights_path,
            )
            logger.info(f"✅ Saved checkpoint for epoch {epoch}")
            self.last_saved_epoch = epoch


def extract_column_names(desc: str) -> list[str]:
    """
    Parses a YOLO-style descriptor string to extract column names, preserving prefixes like 'Box' and 'Mask'.

    Args:
        desc (str): A description string (e.g., "Class Images Instances Box(P R mAP50)").

    Returns:
        list[str]: Parsed column names (e.g., ["Class", "Images", "Instances", "Box(P)", ...]).
    """
    tokens = desc.replace(")", ") ").split()
    final_cols = []

    current_prefix = None
    for token in tokens:
        if "(" in token:
            current_prefix = token.split("(")[0]
            metric = token[token.find("(") + 1 :].rstrip(")")
            final_cols.append(f"{current_prefix}({metric})")
        elif current_prefix:
            final_cols.append(f"{current_prefix}({token.rstrip(')')})")
        else:
            final_cols.append(token)

    return final_cols


def log_confusion_matrix(validator, logger):
    if (
        hasattr(validator, "confusion_matrix")
        and validator.confusion_matrix is not None
    ):
        matrix = validator.confusion_matrix.matrix
        if hasattr(validator, "metrics") and hasattr(
            validator.metrics, "ap_class_index"
        ):
            labelmap = dict(enumerate(list(validator.names.values()) + ["background"]))

        else:
            labelmap = dict(enumerate(validator.names.values()))
        logger.log_confusion_matrix(
            name="confusion_matrix", labelmap=labelmap, matrix=matrix, phase="val"
        )
