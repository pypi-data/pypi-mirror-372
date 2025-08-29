from collections.abc import Callable

import pytest

from picsellia_cv_engine.models.dataset.common.dataset_context import DatasetContext
from picsellia_cv_engine.models.steps.data_validation.common.classification_dataset_context_validator import (
    ClassificationDatasetContextValidator,
)


@pytest.fixture
def mock_classification_dataset_context_validator() -> Callable:
    def _classification_dataset_context_validator(
        dataset_context: DatasetContext,
    ) -> ClassificationDatasetContextValidator:
        return ClassificationDatasetContextValidator(dataset_context=dataset_context)

    return _classification_dataset_context_validator
