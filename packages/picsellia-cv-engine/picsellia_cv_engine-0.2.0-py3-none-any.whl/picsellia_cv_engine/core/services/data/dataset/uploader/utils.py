import json
import os

from picsellia import Datalake
from picsellia.types.enums import ImportAnnotationMode, InferenceType

from picsellia_cv_engine.core.contexts.processing.dataset.picsellia_context import (
    PicselliaDatasetProcessingContext,
)
from picsellia_cv_engine.core.data import (
    CocoDataset,
)


def get_datalake_and_tag(
    context: PicselliaDatasetProcessingContext | None,
    datalake: Datalake | None,
    data_tag: str | None,
):
    """Retrieve datalake and data_tag from context or arguments."""
    if context:
        datalake = context.client.get_datalake(
            name=context.processing_parameters.datalake
        )
        data_tag = context.processing_parameters.data_tag
    if not datalake or not data_tag:
        raise ValueError("datalake and data_tag must not be None")
    return datalake, data_tag


def initialize_coco_data(dataset: CocoDataset):
    """Ensure COCO data is initialized properly."""
    if dataset.coco_data and not dataset.coco_file_path:
        dataset.annotations_dir = dataset.annotations_dir or "temp_annotations"
        os.makedirs(dataset.annotations_dir, exist_ok=True)
        dataset.coco_file_path = os.path.join(
            dataset.annotations_dir, "annotations.json"
        )
        with open(dataset.coco_file_path, "w") as f:
            json.dump(dataset.coco_data, f)

    if dataset.coco_file_path and not dataset.coco_data:
        dataset.coco_data = dataset.load_coco_file_data()
    return dataset


def configure_dataset_type(dataset: CocoDataset, annotations):
    """Configure dataset type if not already set."""
    if dataset.dataset_version.type == InferenceType.NOT_CONFIGURED:
        determine_inference_type(dataset, annotations)


def determine_inference_type(dataset: CocoDataset, annotations: list):
    """Determine and set the inference type based on annotations."""
    first_annotation = annotations[0]
    if "segmentation" in first_annotation and first_annotation["segmentation"]:
        dataset.dataset_version.set_type(InferenceType.SEGMENTATION)
    elif "bbox" in first_annotation and first_annotation["bbox"]:
        dataset.dataset_version.set_type(InferenceType.OBJECT_DETECTION)
    elif "category_id" in first_annotation:
        dataset.dataset_version.set_type(InferenceType.CLASSIFICATION)
    else:
        raise ValueError(f"Unsupported dataset type: {dataset.dataset_version.type}")


def upload_images_and_annotations(
    dataset: CocoDataset,
    datalake: Datalake,
    data_tag: str,
    use_id: bool = True,
    fail_on_asset_not_found: bool = True,
    replace_annotations: bool = False,
):
    """
    Upload dataset based on inference type.

    Supports Classification, Object Detection, and Segmentation inference types.
    """
    upload_images(dataset, datalake, data_tag)
    upload_annotations(dataset, use_id, fail_on_asset_not_found, replace_annotations)


def upload_images(dataset: CocoDataset, datalake: Datalake, data_tag: str):
    """Upload images to the dataset."""
    data_tags: list[str] = [data_tag]
    data = datalake.upload_data(
        filepaths=[
            os.path.join(dataset.images_dir, image_filename)
            for image_filename in os.listdir(dataset.images_dir)
        ],
        tags=data_tags,
    )
    dataset.dataset_version.add_data(data=data)


def upload_annotations(
    dataset: CocoDataset,
    use_id: bool = True,
    fail_on_asset_not_found: bool = True,
    replace_annotations: bool = False,
) -> None:
    """
    Upload annotations based on inference type.

    Supports Classification, Object Detection, and Segmentation inference types.
    """
    dataset.dataset_version.import_annotations_coco_file(
        file_path=dataset.coco_file_path,
        use_id=use_id,
        fail_on_asset_not_found=fail_on_asset_not_found,
        mode=ImportAnnotationMode.REPLACE
        if replace_annotations
        else ImportAnnotationMode.KEEP,
    )
