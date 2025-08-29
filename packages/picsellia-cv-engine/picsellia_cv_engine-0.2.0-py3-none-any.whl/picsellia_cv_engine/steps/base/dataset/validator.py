import logging

from picsellia_cv_engine import step
from picsellia_cv_engine.core import DatasetCollection
from picsellia_cv_engine.core.data import TBaseDataset
from picsellia_cv_engine.core.services.data.dataset.utils import validate_dataset_impl

logger = logging.getLogger(__name__)


@step
def validate_dataset(
    dataset: TBaseDataset | DatasetCollection, fix_annotation: bool = False
):
    """
    Validates a dataset or a dataset collection to ensure data integrity and correctness.

    This function checks each dataset in a collection or a single dataset for any issues. If annotation errors are found,
    it can attempt to fix them based on the provided `fix_annotation` flag. If validation fails for any dataset,
    an error is logged. The validation process is skipped for datasets without a validator.

    Args:
        dataset (Union[TBaseDataset, DatasetCollection]):
            The dataset or dataset collection to validate. If a `DatasetCollection` is provided, each individual dataset
            within the collection will be validated.
        fix_annotation (bool, optional):
            Flag to indicate whether to attempt fixing annotation errors. Defaults to `False`. If set to `True`,
            the function will try to correct any found annotation issues during validation.

    Raises:
        Exception: If validation fails for a dataset in the collection, an error is logged, but the process continues.
    """
    return validate_dataset_impl(dataset=dataset, fix_annotation=fix_annotation)
