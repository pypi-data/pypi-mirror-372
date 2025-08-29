from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset, DatasetCollection, YoloDataset
from picsellia_cv_engine.core.services.data.dataset.utils import (
    load_coco_datasets_impl,
    load_yolo_datasets_impl,
)


@step
def load_coco_datasets(
    use_id: bool = True,
    skip_asset_listing: bool = False,
) -> DatasetCollection[CocoDataset] | CocoDataset:
    """
    A step for loading COCO datasets based on the current pipeline context (training or processing).

    This function adapts to different contexts and loads datasets accordingly:
    - **Training Contexts**: Loads datasets for training, validation, and testing splits.
    - **Processing Contexts**: Loads either a single dataset or multiple datasets depending on the context.

    Args:
        use_id (bool, optional): Whether to use asset UUIDs as filenames when downloading images/annotations.
            If `False`, filenames from the original dataset will be used. Default is `True`.
        skip_asset_listing (bool, optional): Whether to skip listing dataset assets before downloading.
            Default is `False`. This is applicable only for processing contexts.

    Returns:
        Union[DatasetCollection[CocoDataset], CocoDataset]: The loaded dataset(s) based on the context.

            - For **Training Contexts**: Returns a `DatasetCollection[CocoDataset]` containing training, validation,
              and test datasets.
            - For **Processing Contexts**:
                - If both input and output datasets are available, returns a `DatasetCollection[CocoDataset]`.
                - If only an input dataset is available, returns a single `CocoDataset` for the input dataset.

    Raises:
        ValueError:
            - If no datasets are found in the processing context.
            - If the context type is unsupported (neither training nor processing).

    Example:
        - In a **Training Context**, the function loads and prepares datasets for training, validation, and testing.
        - In a **Processing Context**, it loads the input and output datasets (if available) or just the input dataset.
    """
    context = Pipeline.get_active_context()
    return load_coco_datasets_impl(
        context=context, use_id=use_id, skip_asset_listing=skip_asset_listing
    )


@step
def load_yolo_datasets(
    use_id: bool = True,
    skip_asset_listing: bool = False,
) -> DatasetCollection[YoloDataset] | YoloDataset:
    """
    A step for loading YOLO datasets based on the current pipeline context (training or processing).

    This function adapts to different contexts and loads datasets accordingly:
    - **Training Contexts**: Loads datasets for training, validation, and testing splits.
    - **Processing Contexts**: Loads either a single dataset or multiple datasets depending on the context.

    Args:
        use_id (bool, optional): Whether to use asset UUIDs as filenames when downloading images/annotations.
            If `False`, filenames from the original dataset will be used. Default is `True`.
        skip_asset_listing (bool, optional): Whether to skip listing dataset assets before downloading.
            Default is `False`. This is applicable only for processing contexts.

    Returns:
        Union[DatasetCollection[YoloDataset], YoloDataset]: The loaded dataset(s) based on the context.

    Raises:
        ValueError: If no datasets are found or if the context type is unsupported.
    """
    context = Pipeline.get_active_context()
    return load_yolo_datasets_impl(
        context=context, use_id=use_id, skip_asset_listing=skip_asset_listing
    )
