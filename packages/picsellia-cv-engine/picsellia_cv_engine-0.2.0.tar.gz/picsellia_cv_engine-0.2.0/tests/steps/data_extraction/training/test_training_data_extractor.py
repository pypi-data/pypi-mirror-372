from collections.abc import Callable
from unittest.mock import patch

from picsellia.types.enums import InferenceType

from picsellia_cv_engine import Pipeline
from picsellia_cv_engine.enums import DatasetSplitName
from picsellia_cv_engine.models.parameters.augmentation_parameters import (
    AugmentationParameters,
)
from picsellia_cv_engine.models.parameters.export_parameters import ExportParameters
from picsellia_cv_engine.models.parameters.hyper_parameters import HyperParameters
from picsellia_cv_engine.steps.data_extraction.coco_data_extractor import (
    get_coco_dataset_collection,
)
from tests.steps.fixtures.dataset_version_fixtures import DatasetTestMetadata


class TestTrainingDataExtractor:
    def test_training_data_extractor(self, mock_picsellia_training_context: Callable):
        picsellia_training_context = mock_picsellia_training_context(
            experiment_name="test_experiment",
            datasets_metadata=[
                DatasetTestMetadata(
                    dataset_split_name=DatasetSplitName.TRAIN,
                    dataset_type=InferenceType.CLASSIFICATION,
                )
            ],
            hyperparameters_cls=HyperParameters,
            augmentation_parameters_cls=AugmentationParameters,
            export_parameters_cls=ExportParameters,
        )
        with patch.object(Pipeline, "get_active_context") as mock_get_active_context:
            mock_get_active_context.return_value = picsellia_training_context
            dataset_collection = get_coco_dataset_collection.entrypoint()
            assert dataset_collection is not None
