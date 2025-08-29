import os

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.contexts import PicselliaTrainingContext
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.parameters import ExportParameters
from picsellia_cv_engine.core.services.model.utils import evaluate_model_impl
from picsellia_cv_engine.frameworks.ultralytics.model.model import UltralyticsModel
from picsellia_cv_engine.frameworks.ultralytics.parameters.augmentation_parameters import (
    UltralyticsAugmentationParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.parameters.hyper_parameters import (
    UltralyticsHyperParameters,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.predictor.classification import (
    UltralyticsClassificationModelPredictor,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.predictor.object_detection import (
    UltralyticsDetectionModelPredictor,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.predictor.segmentation import (
    UltralyticsSegmentationModelPredictor,
)


@step
def evaluate_ultralytics_model(
    model: UltralyticsModel,
    dataset: TBaseDataset,
) -> None:
    """
    Evaluate an Ultralytics model on a given dataset and log evaluation metrics.

    This step handles evaluation for classification, object detection, and segmentation models trained
    with the Ultralytics framework. It:

    - Retrieves the current training context from the pipeline.
    - Chooses the appropriate predictor class based on the model's task type.
    - Runs inference on the provided dataset in batches.
    - Post-processes predictions into Picsellia-compatible format.
    - Computes evaluation metrics and logs them to the experiment.

    Supported tasks:
        - Classification
        - Object Detection
        - Segmentation

    Args:
        model (UltralyticsModel): The trained Ultralytics model to evaluate.
        dataset (TBaseDataset): The dataset to evaluate the model on.

    Raises:
        ValueError: If the model's task type is unsupported.

    Returns:
        None
    """

    context: PicselliaTrainingContext[
        UltralyticsHyperParameters, UltralyticsAugmentationParameters, ExportParameters
    ] = Pipeline.get_active_context()

    if model.loaded_model.task == "classify":
        model_predictor = UltralyticsClassificationModelPredictor(model=model)
    elif model.loaded_model.task == "detect":
        model_predictor = UltralyticsDetectionModelPredictor(model=model)
    elif model.loaded_model.task == "segment":
        model_predictor = UltralyticsSegmentationModelPredictor(model=model)
    else:
        raise ValueError(f"Model task {model.loaded_model.task} not supported")

    image_paths = model_predictor.pre_process_dataset(dataset=dataset)
    image_batches = model_predictor.prepare_batches(
        image_paths=image_paths, batch_size=context.hyperparameters.batch_size
    )
    batch_results = model_predictor.run_inference_on_batches(
        image_batches=image_batches
    )
    picsellia_predictions = model_predictor.post_process_batches(
        image_batches=image_batches,
        batch_results=batch_results,
        dataset=dataset,
    )

    evaluate_model_impl(
        context=context,
        picsellia_predictions=picsellia_predictions,
        inference_type=model.model_version.type,
        assets=dataset.assets,
        output_dir=os.path.join(context.working_dir, "evaluation"),
        training_labelmap=context.experiment.get_log("labelmap").data,
    )
