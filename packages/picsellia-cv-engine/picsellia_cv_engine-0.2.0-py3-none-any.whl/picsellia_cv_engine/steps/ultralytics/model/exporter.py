import logging

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.contexts import PicselliaTrainingContext
from picsellia_cv_engine.core.parameters import ExportParameters
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.augmentation_parameters import (
    UltralyticsAugmentationParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.exporter import (
    UltralyticsModelExporter,
)

logger = logging.getLogger(__name__)


@step
def export_ultralytics_model(model: UltralyticsModel):
    """
    Export a trained Ultralytics model and save it to the associated experiment.

    This step performs the following:
    - Retrieves the active Picsellia training context.
    - Initializes a model exporter for the given Ultralytics model.
    - Exports the model to the format specified in the export parameters (e.g., ONNX).
    - Saves the exported model as an artifact in the experiment.

    If the model does not have an `exported_weights_dir` set, the function logs a message and skips the export.

    Args:
        model (UltralyticsModel): The trained Ultralytics model to export.

    Logs:
        Skips export if no export destination is defined on the model.
    """
    context: PicselliaTrainingContext[
        UltralyticsHyperParameters, UltralyticsAugmentationParameters, ExportParameters
    ] = Pipeline.get_active_context()

    model_exporter = UltralyticsModelExporter(model=model)

    if model.exported_weights_dir:
        model_exporter.export_model(
            exported_model_destination_path=model.exported_weights_dir,
            export_format=context.export_parameters.export_format,
            hyperparameters=context.hyperparameters,
        )
        model_exporter.save_model_to_experiment(
            experiment=context.experiment,
            exported_weights_path=model.exported_weights_dir,
            exported_weights_name="model-latest",
        )
    else:
        logger.info("No exported weights directory found in model. Skipping export.")
