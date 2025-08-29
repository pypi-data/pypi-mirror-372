from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.services.data.dataset.validator.common import (
    DatasetValidator,
)


class NotConfiguredDatasetValidator(DatasetValidator[TBaseDataset]):
    def validate(self):
        """
        Validate the dataset.

        Raises:
            ValueError: If the dataset is not valid.
        """
        super().validate()
