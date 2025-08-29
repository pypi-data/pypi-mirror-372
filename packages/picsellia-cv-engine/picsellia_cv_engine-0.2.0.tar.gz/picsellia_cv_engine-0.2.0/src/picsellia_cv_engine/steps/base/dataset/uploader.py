import logging

from picsellia import Datalake

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.contexts import PicselliaDatasetProcessingContext
from picsellia_cv_engine.core.services.data.dataset.uploader.utils import (
    configure_dataset_type,
    get_datalake_and_tag,
    initialize_coco_data,
    upload_annotations,
    upload_images,
    upload_images_and_annotations,
)

logger = logging.getLogger(__name__)


@step
def upload_full_dataset(
    dataset: CocoDataset,
    datalake: Datalake | None = None,
    data_tag: str | None = None,
    use_id: bool = True,
    fail_on_asset_not_found: bool = True,
    replace_annotations: bool | None = None,
) -> None:
    """
    Upload both images and annotations for a COCO dataset.

    This step manages the complete dataset upload workflow. It configures the dataset type based on its annotations
    and handles image and annotation upload according to the dataset's inference type (classification, detection, etc.).

    If annotations are present:
    - The dataset type is automatically inferred.
    - Both images and annotations are uploaded.
    - If `replace_annotations` is not explicitly provided, it will be determined from the processing context.

    If annotations are missing:
    - Only images are uploaded.

    Args:
        dataset (CocoDataset): The dataset to upload (including images and optionally annotations).
        datalake (Optional[Datalake]): The target datalake. If not provided, it is inferred from the processing context.
        data_tag (Optional[str]): The tag used to associate the upload in the datalake. Defaults to the one in the context.
        use_id (bool): Whether to use asset IDs for the upload (defaults to True).
        fail_on_asset_not_found (bool): If True, raises an error when a corresponding asset is not found.
        replace_annotations (Optional[bool]): Whether to overwrite existing annotations. Fetched from context if None.
    """
    context: PicselliaDatasetProcessingContext = Pipeline.get_active_context()
    datalake, data_tag = get_datalake_and_tag(
        context=context, datalake=datalake, data_tag=data_tag
    )

    dataset = initialize_coco_data(dataset=dataset)
    annotations = dataset.coco_data.get("annotations", [])

    if annotations:
        if not replace_annotations:
            context = Pipeline.get_active_context()
            if hasattr(context.processing_parameters, "replace_annotations"):
                replace_annotations = context.processing_parameters.replace_annotations
            else:
                replace_annotations = False
                logger.info("replace_annotations is not set, defaulting to False")
        configure_dataset_type(dataset=dataset, annotations=annotations)
        upload_images_and_annotations(
            dataset=dataset,
            datalake=datalake,
            data_tag=data_tag,
            use_id=use_id,
            fail_on_asset_not_found=fail_on_asset_not_found,
            replace_annotations=replace_annotations,
        )
    else:
        upload_images(dataset=dataset, datalake=datalake, data_tag=data_tag)


@step
def upload_dataset_images(
    dataset: CocoDataset,
    datalake: Datalake | None = None,
    data_tag: str | None = None,
) -> None:
    """
    Upload only the image files from a COCO dataset.

    This step uploads all image assets associated with the provided dataset to the datalake.
    Annotation data, if present, is ignored.

    Args:
        dataset (CocoDataset): The dataset whose image files should be uploaded.
        datalake (Optional[Datalake]): The target datalake. Inferred from the context if not provided.
        data_tag (Optional[str]): Optional tag to associate with the uploaded data. Inferred from the context if not provided.
    """
    context: PicselliaDatasetProcessingContext = Pipeline.get_active_context()
    datalake, data_tag = get_datalake_and_tag(
        context=context, datalake=datalake, data_tag=data_tag
    )

    upload_images(dataset=dataset, datalake=datalake, data_tag=data_tag)


@step
def upload_dataset_annotations(
    dataset: CocoDataset,
    use_id: bool = True,
    fail_on_asset_not_found: bool = True,
    replace_annotations: bool | None = None,
) -> None:
    """
    Upload only the annotations from a COCO dataset.

    This step uploads only the annotations portion of a dataset, based on its inference type.
    It configures the dataset type (e.g., classification, detection, etc.) based on the annotations present.

    If `replace_annotations` is not explicitly provided, the value is taken from the processing parameters context.

    Args:
        dataset (CocoDataset): The dataset containing annotations to upload.
        use_id (bool): Whether to use asset IDs for the upload. Defaults to True.
        fail_on_asset_not_found (bool): Whether to fail if an asset referenced in the annotations is missing. Defaults to True.
        replace_annotations (Optional[bool]): Whether to overwrite existing annotations. Fetched from context if not provided.
    """

    dataset = initialize_coco_data(dataset=dataset)
    annotations = dataset.coco_data.get("annotations", [])

    if annotations:
        if not replace_annotations:
            context = Pipeline.get_active_context()
            if hasattr(context.processing_parameters, "replace_annotations"):
                replace_annotations = context.processing_parameters.replace_annotations
            else:
                replace_annotations = False
                logger.info("replace_annotations is not set, defaulting to False")
        configure_dataset_type(dataset=dataset, annotations=annotations)
        upload_annotations(
            dataset=dataset,
            use_id=use_id,
            fail_on_asset_not_found=fail_on_asset_not_found,
            replace_annotations=replace_annotations,
        )
