import logging
import os

from picsellia_cv_engine.core import CocoDataset, DatasetCollection, YoloDataset
from picsellia_cv_engine.core.contexts import (
    LocalDatasetProcessingContext,
    LocalTrainingContext,
    PicselliaDatasetProcessingContext,
    PicselliaTrainingContext,
)
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.services.data.dataset.loader import (
    TrainingDatasetCollectionExtractor,
)
from picsellia_cv_engine.core.services.data.dataset.validator.utils import (
    get_dataset_validator,
)
from picsellia_cv_engine.core.services.utils.dataset_logging import log_labelmap

logger = logging.getLogger(__name__)


def load_coco_datasets_impl(
    context: PicselliaTrainingContext
    | LocalTrainingContext
    | PicselliaDatasetProcessingContext
    | LocalDatasetProcessingContext,
    use_id: bool,
    skip_asset_listing: bool,
) -> DatasetCollection[CocoDataset] | CocoDataset:
    """
    Implementation logic to load COCO datasets depending on the pipeline context type.

    Handles both training and processing contexts and downloads assets and annotations accordingly.

    Args:
        context: Either a training or processing context instance.
        use_id (bool): Whether to preserve the original asset UUIDs when naming files (instead of filenames).
        skip_asset_listing (bool): Whether to skip asset listing before download.

    Returns:
        DatasetCollection[CocoDataset] or CocoDataset: The loaded dataset(s).

    Raises:
        ValueError: If no datasets are found or an unsupported context is provided.
    """
    # Training Context Handling
    if isinstance(context, PicselliaTrainingContext | LocalTrainingContext):
        dataset_collection_extractor = TrainingDatasetCollectionExtractor(
            experiment=context.experiment,
            train_set_split_ratio=context.hyperparameters.train_set_split_ratio,
        )

        dataset_collection = dataset_collection_extractor.get_dataset_collection(
            context_class=CocoDataset,
            random_seed=context.hyperparameters.seed,
        )

        log_labelmap(
            labelmap=dataset_collection["train"].labelmap,
            experiment=context.experiment,
            log_name="labelmap",
        )

        dataset_collection.dataset_path = os.path.join(context.working_dir, "dataset")

        dataset_collection.download_all(
            images_destination_dir=os.path.join(
                dataset_collection.dataset_path, "images"
            ),
            annotations_destination_dir=os.path.join(
                dataset_collection.dataset_path, "annotations"
            ),
            use_id=use_id,
            skip_asset_listing=False,
        )

        return dataset_collection

    # Processing Context Handling
    elif isinstance(
        context, PicselliaDatasetProcessingContext | LocalDatasetProcessingContext
    ):
        # If both input and output datasets are available
        if (
            context.input_dataset_version_id
            and context.output_dataset_version_id
            and not context.input_dataset_version_id
            == context.output_dataset_version_id
        ):
            input_dataset = CocoDataset(
                name="input",
                dataset_version=context.input_dataset_version,
                assets=context.input_dataset_version.list_assets(),
                labelmap=None,
            )
            output_dataset = CocoDataset(
                name="output",
                dataset_version=context.output_dataset_version,
                assets=None,
                labelmap=None,
            )
            dataset_collection = DatasetCollection([input_dataset, output_dataset])
            dataset_collection.download_all(
                images_destination_dir=os.path.join(context.working_dir, "images"),
                annotations_destination_dir=os.path.join(
                    context.working_dir, "annotations"
                ),
                use_id=use_id,
                skip_asset_listing=skip_asset_listing,
            )
            return dataset_collection

        # If only input dataset is available
        elif (
            context.input_dataset_version_id
            and context.input_dataset_version_id == context.output_dataset_version_id
        ) or (
            context.input_dataset_version_id and not context.output_dataset_version_id
        ):
            dataset = CocoDataset(
                name="input",
                dataset_version=context.input_dataset_version,
                assets=context.input_dataset_version.list_assets(),
                labelmap=None,
            )

            dataset.download_assets(
                destination_dir=os.path.join(
                    context.working_dir, "images", dataset.name
                ),
                use_id=use_id,
                skip_asset_listing=skip_asset_listing,
            )
            dataset.download_annotations(
                destination_dir=os.path.join(
                    context.working_dir, "annotations", dataset.name
                ),
                use_id=use_id,
            )

            return dataset

        else:
            raise ValueError("No datasets found in the processing context.")

    else:
        raise ValueError(f"Unsupported context type: {type(context)}")


def load_yolo_datasets_impl(
    context: PicselliaTrainingContext
    | LocalTrainingContext
    | PicselliaDatasetProcessingContext
    | LocalDatasetProcessingContext,
    use_id: bool,
    skip_asset_listing: bool,
) -> DatasetCollection[YoloDataset] | YoloDataset:
    """
    Implementation logic to load YOLO datasets depending on the pipeline context type.

    Handles both training and processing contexts and downloads assets and annotations accordingly.

    Args:
        context: Either a training or processing context instance.
        use_id (bool): Whether to preserve the original asset UUIDs when naming files (instead of filenames).
        skip_asset_listing (bool): Whether to skip asset listing before download.

    Returns:
        DatasetCollection[YoloDataset] or YoloDataset: The loaded dataset(s).

    Raises:
        ValueError: If no datasets are found or an unsupported context is provided.
    """
    # Training Context Handling
    if isinstance(context, PicselliaTrainingContext | LocalTrainingContext):
        dataset_collection_extractor = TrainingDatasetCollectionExtractor(
            experiment=context.experiment,
            train_set_split_ratio=context.hyperparameters.train_set_split_ratio,
        )

        dataset_collection = dataset_collection_extractor.get_dataset_collection(
            context_class=YoloDataset,
            random_seed=context.hyperparameters.seed,
        )

        log_labelmap(
            labelmap=dataset_collection["train"].labelmap,
            experiment=context.experiment,
            log_name="labelmap",
        )

        dataset_collection.dataset_path = os.path.join(context.working_dir, "dataset")

        dataset_collection.download_all(
            images_destination_dir=os.path.join(
                dataset_collection.dataset_path, "images"
            ),
            annotations_destination_dir=os.path.join(
                dataset_collection.dataset_path, "labels"
            ),
            use_id=use_id,
            skip_asset_listing=False,
        )

        return dataset_collection

    # Processing Context Handling
    elif isinstance(
        context, PicselliaDatasetProcessingContext | LocalDatasetProcessingContext
    ):
        # If both input and output datasets are available
        if (
            context.input_dataset_version_id
            and context.output_dataset_version_id
            and not context.input_dataset_version_id
            == context.output_dataset_version_id
        ):
            input_dataset = YoloDataset(
                name="input",
                dataset_version=context.input_dataset_version,
                assets=context.input_dataset_version.list_assets(),
                labelmap=None,
            )
            output_dataset = YoloDataset(
                name="output",
                dataset_version=context.output_dataset_version,
                assets=None,
                labelmap=None,
            )
            dataset_collection = DatasetCollection([input_dataset, output_dataset])
            dataset_collection.download_all(
                images_destination_dir=os.path.join(context.working_dir, "images"),
                annotations_destination_dir=os.path.join(context.working_dir, "labels"),
                use_id=use_id,
                skip_asset_listing=skip_asset_listing,
            )
            return dataset_collection

        # If only input dataset is available
        elif (
            context.input_dataset_version_id
            and context.input_dataset_version_id == context.output_dataset_version_id
        ) or (
            context.input_dataset_version_id and not context.output_dataset_version_id
        ):
            dataset = YoloDataset(
                name="input",
                dataset_version=context.input_dataset_version,
                assets=context.input_dataset_version.list_assets(),
                labelmap=None,
            )

            dataset.download_assets(
                destination_dir=os.path.join(
                    context.working_dir, "images", dataset.name
                ),
                use_id=use_id,
                skip_asset_listing=skip_asset_listing,
            )
            dataset.download_annotations(
                destination_dir=os.path.join(
                    context.working_dir, "labels", dataset.name
                ),
                use_id=use_id,
            )

            return dataset

        else:
            raise ValueError("No datasets found in the processing context.")

    else:
        raise ValueError(f"Unsupported context type: {type(context)}")


def validate_dataset_impl(
    dataset: TBaseDataset | DatasetCollection, fix_annotation: bool = False
):
    validators = {}

    if not isinstance(dataset, DatasetCollection):
        validator = get_dataset_validator(
            dataset=dataset, fix_annotation=fix_annotation
        )
        if validator:
            validator.validate()
    else:
        dataset_collection = dataset

        for name, dataset in dataset_collection.datasets.items():
            try:
                validator = get_dataset_validator(
                    dataset=dataset, fix_annotation=fix_annotation
                )
                if validator:
                    validator.validate()
                    validators[name] = validator
                else:
                    logger.info(f"Skipping validation for dataset '{name}'.")
            except Exception as e:
                logger.error(f"Validation failed for dataset '{name}': {str(e)}")
