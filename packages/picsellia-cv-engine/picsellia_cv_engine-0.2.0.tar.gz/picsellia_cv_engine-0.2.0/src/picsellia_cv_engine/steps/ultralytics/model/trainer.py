import os

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import DatasetCollection
from picsellia_cv_engine.core.contexts import PicselliaTrainingContext
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.parameters import ExportParameters
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.augmentation_parameters import (
    UltralyticsAugmentationParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.trainer import (
    UltralyticsModelTrainer,
)


@step
def train_ultralytics_model(
    model: UltralyticsModel,
    dataset_collection: DatasetCollection[TBaseDataset],
) -> UltralyticsModel:
    """
    Train an Ultralytics model using the provided dataset collection and training context.

    This step:
    - Retrieves the active training context to access hyperparameters, augmentation settings, and experiment metadata.
    - Initializes an `UltralyticsModelTrainer` to handle the training logic.
    - Runs the training pipeline on the dataset collection.
    - Sets the latest run directory and locates the best model weights after training.
    - Saves the trained model weights as an artifact in the experiment.

    Args:
        model (UltralyticsModel): The model instance to be trained.
        dataset_collection (DatasetCollection[TBaseDataset]): The dataset collection used for training,
            typically including 'train', 'val', and optionally 'test' datasets.

    Returns:
        UltralyticsModel: The trained model with updated internal state and trained weights.

    Raises:
        FileNotFoundError: If the trained weights are not found after training.
    """
    context: PicselliaTrainingContext[
        UltralyticsHyperParameters, UltralyticsAugmentationParameters, ExportParameters
    ] = Pipeline.get_active_context()

    model_trainer = UltralyticsModelTrainer(
        model=model,
        experiment=context.experiment,
    )

    model = model_trainer.train_model(
        dataset_collection=dataset_collection,
        hyperparameters=context.hyperparameters,
        augmentation_parameters=context.augmentation_parameters,
    )

    model.set_latest_run_dir()
    model.set_trained_weights_path()
    if not model.trained_weights_path or not os.path.exists(model.trained_weights_path):
        raise FileNotFoundError(
            f"Trained weights not found at {model.trained_weights_path}"
        )
    model.save_artifact_to_experiment(
        experiment=context.experiment,
        artifact_name="best-model",
        artifact_path=model.trained_weights_path,
    )

    return model
