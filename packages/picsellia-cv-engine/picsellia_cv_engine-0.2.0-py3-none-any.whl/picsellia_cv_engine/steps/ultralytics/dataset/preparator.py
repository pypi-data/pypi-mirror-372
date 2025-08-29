from picsellia.types.enums import InferenceType

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import DatasetCollection
from picsellia_cv_engine.core.services.data.dataset.utils import (
    load_coco_datasets_impl,
    load_yolo_datasets_impl,
    validate_dataset_impl,
)
from picsellia_cv_engine.frameworks.ultralytics.services.data.utils import (
    detect_inference_type_from_experiment,
    generate_data_yaml,
    prepare_classification_data,
)


@step
def prepare_ultralytics_dataset() -> DatasetCollection:
    """
    Prepare and validate a dataset for training with the Ultralytics framework.

    This step dynamically selects the appropriate dataset loading and formatting strategy based on
    the inference task type (classification, object detection, or segmentation) detected from the
    current experiment context.

    Processing includes:
    - Loading COCO-style datasets for classification tasks and restructuring them into class-based folders.
    - Loading YOLO-style datasets for detection and segmentation tasks, followed by generating a `data.yaml` file.
    - Validating the dataset and optionally fixing annotation issues.

    Returns:
        DatasetCollection: A dataset collection object ready for use in training pipelines.

    Raises:
        ValueError: If the task type is unsupported or cannot be inferred from the experiment.
    """
    context = Pipeline.get_active_context()
    task_type: InferenceType = detect_inference_type_from_experiment(context.experiment)

    if task_type == InferenceType.CLASSIFICATION:
        dataset_collection = load_coco_datasets_impl(
            context=context, skip_asset_listing=False
        )
        dataset_collection = prepare_classification_data(
            dataset_collection=dataset_collection
        )
    elif task_type in (InferenceType.OBJECT_DETECTION, InferenceType.SEGMENTATION):
        dataset_collection = load_yolo_datasets_impl(
            context=context, skip_asset_listing=False
        )
        dataset_collection = generate_data_yaml(dataset_collection=dataset_collection)
    else:
        raise ValueError(f"Unsupported task type detected: {task_type}")
    validate_dataset_impl(dataset=dataset_collection, fix_annotation=True)
    return dataset_collection
