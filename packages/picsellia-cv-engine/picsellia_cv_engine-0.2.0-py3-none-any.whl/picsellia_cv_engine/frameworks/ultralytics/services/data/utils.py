import os

import yaml
from picsellia import Experiment
from picsellia.types.enums import InferenceType

from picsellia_cv_engine import Pipeline
from picsellia_cv_engine.core import CocoDataset, DatasetCollection, YoloDataset
from picsellia_cv_engine.core.services.data.dataset.preprocessing import (
    ClassificationBaseDatasetPreparator,
)


def detect_inference_type_from_experiment(experiment: Experiment) -> InferenceType:
    """
    Detects the inference type from the types of all attached dataset versions.
    Ensures all attached datasets are of the same type, otherwise raises an error.

    Args:
        experiment (Experiment): The experiment to inspect.

    Returns:
        InferenceType: The common inference type of all attached datasets.

    Raises:
        ValueError: If the attached datasets have different types.
    """
    dataset_versions = experiment.list_attached_dataset_versions()
    dataset_types = {ds.type for ds in dataset_versions}

    if len(dataset_types) == 1:
        return dataset_types.pop()
    else:
        raise ValueError(
            f"Multiple dataset types detected in experiment: {dataset_types}. "
            f"Please ensure all attached datasets are of the same type."
        )


def generate_data_yaml(
    dataset_collection: DatasetCollection[YoloDataset],
) -> DatasetCollection[YoloDataset]:
    data_yaml = {
        "train": os.path.join(dataset_collection.dataset_path, "images", "train"),
        "val": os.path.join(dataset_collection.dataset_path, "images", "val"),
        "test": os.path.join(dataset_collection.dataset_path, "images", "test"),
        "nc": len(dataset_collection["train"].labelmap.keys()),
        "names": list(dataset_collection["train"].labelmap.keys()),
    }

    with open(os.path.join(dataset_collection.dataset_path, "data.yaml"), "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    return dataset_collection


def prepare_classification_data(
    dataset_collection: DatasetCollection[CocoDataset],
) -> DatasetCollection[CocoDataset]:
    """
    Prepares and organizes a dataset collection for Ultralytics classification tasks.

    This function iterates over each dataset in the provided `DatasetCollection`, organizing them
    using the `ClassificationDatasetPreparator` to structure the dataset for use with Ultralytics classification.
    Each dataset is moved into a new directory, with the structure suitable for Ultralytics training.

    Args:
        dataset_collection (DatasetCollection): The original dataset collection to be prepared for classification.

    Returns:
        DatasetCollection: A dataset collection where each dataset has been organized and prepared for Ultralytics classification tasks.
    """
    context = Pipeline.get_active_context()
    for dataset in dataset_collection:
        destination_dir = str(
            os.path.join(
                context.working_dir,
                "ultralytics_dataset",
                dataset.name,
            )
        )
        preparator = ClassificationBaseDatasetPreparator(
            dataset=dataset,
            destination_dir=destination_dir,
        )
        prepared_dataset = preparator.organize()

        dataset_collection[prepared_dataset.name] = prepared_dataset

    dataset_collection.dataset_path = os.path.join(
        context.working_dir, "ultralytics_dataset"
    )

    return dataset_collection
