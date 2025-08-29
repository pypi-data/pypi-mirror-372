import logging

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.contexts import PicselliaTrainingContext
from picsellia_cv_engine.core.parameters import ExportParameters
from picsellia_cv_engine.core.services.model.utils import build_model_impl
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.augmentation_parameters import (
    UltralyticsAugmentationParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)

logger = logging.getLogger(__name__)


@step
def load_ultralytics_model(
    pretrained_weights_name: str,
    trained_weights_name: str | None = None,
    config_name: str | None = None,
    exported_weights_name: str | None = None,
) -> UltralyticsModel:
    """
    Load an Ultralytics YOLO model with the specified weights and configurations.

    This step:
    - Retrieves the current training context from the pipeline.
    - Initializes an `UltralyticsModel` using metadata from the experiment and optional weight/config names.
    - Downloads the pretrained weights and loads them using Ultralytics' `YOLO` API.
    - Sets the loaded model into the `UltralyticsModel` instance for downstream training or inference.

    Args:
        pretrained_weights_name (str): The name of the pretrained weights file to load.
        trained_weights_name (str, optional): Name of the trained weights (if resuming training or fine-tuning).
        config_name (str, optional): Name of the configuration file used for the model.
        exported_weights_name (str, optional): Name of the exported weights (e.g., for inference/export steps).

    Returns:
        UltralyticsModel: An initialized model with its architecture and weights loaded.

    Raises:
        FileNotFoundError: If the pretrained weights path is not found in the model after initialization.
    """
    context: PicselliaTrainingContext[
        UltralyticsHyperParameters, UltralyticsAugmentationParameters, ExportParameters
    ] = Pipeline.get_active_context()

    model = build_model_impl(
        context=context,
        model_cls=UltralyticsModel,
        pretrained_weights_name=pretrained_weights_name,
        trained_weights_name=trained_weights_name,
        config_name=config_name,
        exported_weights_name=exported_weights_name,
    )

    if not model.pretrained_weights_path:
        raise FileNotFoundError("No pretrained weights path found in model.")

    loaded_model = model.load_yolo_weights(
        weights_path=model.pretrained_weights_path,
        device=context.hyperparameters.device,
    )
    model.set_loaded_model(loaded_model)
    return model
