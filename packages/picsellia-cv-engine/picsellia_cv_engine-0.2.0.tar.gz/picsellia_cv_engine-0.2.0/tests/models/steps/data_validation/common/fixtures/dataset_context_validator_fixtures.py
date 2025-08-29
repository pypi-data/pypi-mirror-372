from collections.abc import Callable

import pytest

from picsellia_cv_engine.models.dataset.common.dataset_context import DatasetContext
from picsellia_cv_engine.models.steps.data_validation.common.dataset_context_validator import (
    DatasetContextValidator,
)


@pytest.fixture
def mock_dataset_context_validator() -> Callable:
    def _dataset_context_validator(
        dataset_context: DatasetContext,
    ) -> DatasetContextValidator:
        return DatasetContextValidator(dataset_context=dataset_context)

    return _dataset_context_validator
