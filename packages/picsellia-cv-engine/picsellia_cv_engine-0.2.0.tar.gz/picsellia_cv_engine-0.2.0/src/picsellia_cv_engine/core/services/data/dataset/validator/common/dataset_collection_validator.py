from picsellia_cv_engine.core import DatasetCollection
from picsellia_cv_engine.core.services.data.dataset.validator.common import (
    DatasetValidator,
)


class DatasetCollectionValidator:
    """
    Validates various aspects of a dataset collection.

    This class performs common validation tasks for dataset collections, including checking for image extraction
    completeness, image format, image corruption, and annotation integrity.

    Attributes:
        dataset_collection (DatasetCollection): The dataset collection to validate.
        dataset_validator (Type[DatasetValidator]): The validator class for individual datasets.
    """

    def __init__(
        self,
        dataset_collection: DatasetCollection,
        dataset_validator: type[DatasetValidator],
    ):
        """
        Initializes the DatasetCollectionValidator with a dataset collection to validate.

        Parameters:
            dataset_collection (DatasetCollection): The dataset collection to validate.
            dataset_validator (Type[DatasetValidator]): The class used to validate individual datasets.
        """
        self.dataset_collection = dataset_collection
        self.dataset_validator = dataset_validator

    def validate(self, fix_annotation: bool = False) -> None:
        """
        Validates the dataset collection.

        Iterates through the datasets in the collection and applies the context validator
        for each dataset.
        """
        for dataset in self.dataset_collection:
            validator = self.dataset_validator(
                dataset=dataset, fix_annotation=fix_annotation
            )
            validator.validate()
