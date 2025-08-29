import os
from typing import TypeVar

from picsellia import Experiment

from picsellia_cv_engine.core import DatasetCollection
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.augmentation_parameters import (
    UltralyticsAugmentationParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.callbacks import (
    UltralyticsCallbacks,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.classification import (
    UltralyticsClassificationLogger,
    UltralyticsClassificationMetricMapping,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.object_detection import (
    UltralyticsObjectDetectionLogger,
    UltralyticsObjectDetectionMetricMapping,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.segmentation import (
    UltralyticsSegmentationLogger,
    UltralyticsSegmentationMetricMapping,
)

TUltralyticsCallbacks = TypeVar("TUltralyticsCallbacks", bound=UltralyticsCallbacks)


class UltralyticsModelTrainer:
    """
    Trainer class for managing the training lifecycle of a model using the Ultralytics framework.

    This class handles the setup of callbacks, integration with the Picsellia experiment system,
    and executes training using specific hyperparameters and augmentations.
    """

    def __init__(
        self,
        model: UltralyticsModel,
        experiment: Experiment,
    ):
        """
        Initializes the trainer with a model and an experiment.

        Args:
            model (UltralyticsModel): The model to be trained.
            experiment (Experiment): The experiment instance used for logging and tracking results.
        """
        self.model = model
        self.experiment = experiment

    def _setup_callbacks(
        self,
        callbacks: type[TUltralyticsCallbacks] = UltralyticsCallbacks,
        save_period: int = 10,
    ):
        """
        Sets up the appropriate callbacks depending on the model task.

        Args:
            callbacks (type): Callback handler class to use.
            save_period (int): Number of epochs between model checkpoint saves.

        Raises:
            ValueError: If the model task is not supported.
        """
        if self.model.loaded_model.task == "classify":
            callback_handler = callbacks(
                experiment=self.experiment,
                logger=UltralyticsClassificationLogger,
                metric_mapping=UltralyticsClassificationMetricMapping(),
                model=self.model,
                save_period=save_period,
            )
        elif self.model.loaded_model.task == "detect":
            callback_handler = callbacks(
                experiment=self.experiment,
                logger=UltralyticsObjectDetectionLogger,
                metric_mapping=UltralyticsObjectDetectionMetricMapping(),
                model=self.model,
                save_period=save_period,
            )
        elif self.model.loaded_model.task == "segment":
            callback_handler = callbacks(
                experiment=self.experiment,
                logger=UltralyticsSegmentationLogger,
                metric_mapping=UltralyticsSegmentationMetricMapping(),
                model=self.model,
                save_period=save_period,
            )
        else:
            raise ValueError(f"Unsupported task: {self.model.loaded_model.task}")
        for event, callback in callback_handler.get_callbacks().items():
            self.model.loaded_model.add_callback(event, callback)

    def train_model(
        self,
        dataset_collection: DatasetCollection[TBaseDataset],
        hyperparameters: UltralyticsHyperParameters,
        augmentation_parameters: UltralyticsAugmentationParameters,
        callbacks: type[TUltralyticsCallbacks] = UltralyticsCallbacks,
    ) -> UltralyticsModel:
        """
        Executes training on the model using the provided datasets and parameters.

        Args:
            dataset_collection (DatasetCollection): Dataset used for training and validation.
            hyperparameters (UltralyticsHyperParameters): Training configuration including learning rate, epochs, etc.
            augmentation_parameters (UltralyticsAugmentationParameters): Data augmentation parameters.
            callbacks (type): Callback class to use for logging and event handling.

        Returns:
            UltralyticsModel: The trained model instance.
        """
        self._setup_callbacks(
            callbacks=callbacks, save_period=hyperparameters.save_period
        )

        if self.model.loaded_model.task == "classify":
            data = dataset_collection.dataset_path
        else:
            data = os.path.join(dataset_collection.dataset_path, "data.yaml")

        if hyperparameters.epochs > 0:
            self.model.loaded_model.train(
                # Hyperparameters
                data=data,
                epochs=hyperparameters.epochs,
                time=hyperparameters.time,
                patience=hyperparameters.patience,
                batch=hyperparameters.batch_size,
                imgsz=hyperparameters.image_size,
                save=True,
                save_period=hyperparameters.save_period,
                cache=hyperparameters.cache,
                device=hyperparameters.device,
                workers=hyperparameters.workers,
                project=self.model.results_dir,
                name=self.model.name,
                exist_ok=True,
                pretrained=True,
                optimizer=hyperparameters.optimizer,
                seed=hyperparameters.seed,
                deterministic=hyperparameters.deterministic,
                single_cls=hyperparameters.single_cls,
                rect=hyperparameters.rect,
                cos_lr=hyperparameters.cos_lr,
                close_mosaic=hyperparameters.close_mosaic,
                amp=hyperparameters.amp,
                fraction=hyperparameters.fraction,
                profile=hyperparameters.profile,
                freeze=hyperparameters.freeze,
                lr0=hyperparameters.lr0,
                lrf=hyperparameters.lrf,
                momentum=hyperparameters.momentum,
                weight_decay=hyperparameters.weight_decay,
                warmup_epochs=hyperparameters.warmup_epochs,
                warmup_momentum=hyperparameters.warmup_momentum,
                warmup_bias_lr=hyperparameters.warmup_bias_lr,
                box=hyperparameters.box,
                cls=hyperparameters.cls,
                dfl=hyperparameters.dfl,
                pose=hyperparameters.pose,
                kobj=hyperparameters.kobj,
                label_smoothing=hyperparameters.label_smoothing,
                nbs=hyperparameters.nbs,
                overlap_mask=hyperparameters.overlap_mask,
                mask_ratio=hyperparameters.mask_ratio,
                dropout=hyperparameters.dropout,
                val=hyperparameters.validate,
                plots=hyperparameters.plots,
                # Augmentation parameters
                hsv_h=augmentation_parameters.hsv_h,
                hsv_s=augmentation_parameters.hsv_s,
                hsv_v=augmentation_parameters.hsv_v,
                degrees=augmentation_parameters.degrees,
                translate=augmentation_parameters.translate,
                scale=augmentation_parameters.scale,
                shear=augmentation_parameters.shear,
                perspective=augmentation_parameters.perspective,
                flipud=augmentation_parameters.flipud,
                fliplr=augmentation_parameters.fliplr,
                bgr=augmentation_parameters.bgr,
                mosaic=augmentation_parameters.mosaic,
                mixup=augmentation_parameters.mixup,
                copy_paste=augmentation_parameters.copy_paste,
                auto_augment=augmentation_parameters.auto_augment,
                erasing=augmentation_parameters.erasing,
                crop_fraction=augmentation_parameters.crop_fraction,
            )

        return self.model
