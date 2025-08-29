import json
from typing import Any

from picsellia import Asset, Experiment
from picsellia.sdk.asset import MultiAsset
from picsellia.sdk.evaluation import MultiEvaluation
from picsellia.types.enums import InferenceType
from pycocotools.coco import COCO
from tqdm import tqdm


def save_json(coco_data: dict, output_path: str) -> None:
    with open(output_path, "w") as f:
        json.dump(coco_data, f, indent=4)


def get_asset(id, connexion, dataset_version_id) -> Asset:
    r = connexion.get(f"/api/asset/{id}").json()
    return Asset(connexion, dataset_version_id, r)


def flatten_segmentation(segmentation: list[list[float]]) -> list[float]:
    if not segmentation or not isinstance(segmentation, list):
        return []
    return [coord for point in segmentation for coord in point]


def compute_bbox_and_area_from_polygon(
    flattened_polygon: list[float],
) -> tuple[list[float], float]:
    x_coords = flattened_polygon[0::2]
    y_coords = flattened_polygon[1::2]
    x_min = min(x_coords)
    y_min = min(y_coords)
    x_max = max(x_coords)
    y_max = max(y_coords)
    w = x_max - x_min
    h = y_max - y_min
    area = w * h
    return [x_min, y_min, w, h], area


def extract_prediction_list(
    evaluation_info: dict, inference_type: InferenceType
) -> list[dict]:
    if inference_type == InferenceType.OBJECT_DETECTION:
        return evaluation_info["rectangles"]
    elif inference_type == InferenceType.SEGMENTATION:
        return evaluation_info["polygons"]
    elif inference_type == InferenceType.CLASSIFICATION:
        return evaluation_info["classifications"]
    else:
        raise ValueError(f"Unsupported inference type: {inference_type}")


def build_annotation(
    pred,
    image_id,
    label_name,
    category_id,
    annotation_id,
    inference_type: InferenceType,
) -> dict:
    if inference_type == InferenceType.OBJECT_DETECTION:
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": [pred["x"], pred["y"], pred["w"], pred["h"]],
            "area": pred["w"] * pred["h"],
            "score": pred["score"],
            "iscrowd": 0,
        }
    elif inference_type == InferenceType.SEGMENTATION:
        segmentation_flat = flatten_segmentation(pred["polygon"])
        bbox, area = compute_bbox_and_area_from_polygon(segmentation_flat)
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": [segmentation_flat],
            "bbox": bbox,
            "area": area,
            "score": pred["score"],
            "iscrowd": 0,
        }
    elif inference_type == InferenceType.CLASSIFICATION:
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "score": pred["score"],
        }
    else:
        raise ValueError(f"Unsupported inference type: {inference_type}")


def generate_coco_predictions(
    evaluations: MultiEvaluation,
    image_name_map: dict[str, int],
    label_name_map: dict[str, int],
    categories: list[dict],
    gt_coco_path: str,
    inference_type: InferenceType,
) -> dict:
    gt_coco = COCO(gt_coco_path)
    gt_image_ids = {img["id"] for img in gt_coco.loadImgs(gt_coco.getImgIds())}

    images, annotations = [], []
    annotation_id = 1
    label_counter = len(label_name_map)

    for evaluation in tqdm(evaluations, desc="Processing prediction evaluations"):
        evaluation_info = evaluation.sync()
        asset_info = evaluation_info["asset"]
        filename = asset_info["data"]["filename"]
        if (
            filename not in image_name_map
            or image_name_map[filename] not in gt_image_ids
        ):
            continue

        image_id = image_name_map[filename]
        image_info = {
            "id": image_id,
            "file_name": filename,
            "width": asset_info["data"]["meta"]["width"],
            "height": asset_info["data"]["meta"]["height"],
        }
        if image_info not in images:
            images.append(image_info)

        for pred in extract_prediction_list(evaluation_info, inference_type):
            label_name = pred["label"]["name"]
            if label_name not in label_name_map:
                label_name_map[label_name] = label_counter
                categories.append({"id": label_counter, "name": label_name})
                label_counter += 1

            category_id = label_name_map[label_name]
            annotations.append(
                build_annotation(
                    pred,
                    image_id,
                    label_name,
                    category_id,
                    annotation_id,
                    inference_type,
                )
            )
            annotation_id += 1

    return {"images": images, "annotations": annotations, "categories": categories}


def extract_asset_annotations(asset, inference_type: InferenceType) -> list[Any]:
    annotations = asset.list_annotations()
    if not annotations:
        return []
    if inference_type == InferenceType.OBJECT_DETECTION:
        return annotations[0].list_rectangles()
    elif inference_type == InferenceType.SEGMENTATION:
        return annotations[0].list_polygons()
    elif inference_type == InferenceType.CLASSIFICATION:
        return annotations[0].list_classifications()
    else:
        raise ValueError(f"Unsupported inference type: {inference_type}")


def build_gt_annotation(
    ann,
    image_id: int,
    label_name: str,
    category_id: int,
    annotation_id: int,
    inference_type: InferenceType,
) -> dict:
    if inference_type == InferenceType.OBJECT_DETECTION:
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": [ann.x, ann.y, ann.w, ann.h],
            "area": ann.w * ann.h,
            "iscrowd": 0,
        }
    elif inference_type == InferenceType.SEGMENTATION:
        segmentation_flat = flatten_segmentation(ann.coords)
        bbox, area = compute_bbox_and_area_from_polygon(segmentation_flat)
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": [segmentation_flat],
            "bbox": bbox,
            "area": area,
            "iscrowd": 0,
        }
    elif inference_type == InferenceType.CLASSIFICATION:
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
        }
    else:
        raise ValueError(f"Unsupported inference type: {inference_type}")


def generate_coco_ground_truth(
    assets: list[Asset] | MultiAsset,
    image_name_map: dict[str, int],
    label_name_map: dict[str, int],
    categories: list[dict],
    inference_type: InferenceType,
) -> tuple[dict, dict[str, int], dict[str, int], list[dict]]:
    images, annotations = [], []
    annotation_id = 1
    image_counter = len(image_name_map)
    label_counter = len(label_name_map)

    for asset in tqdm(assets, desc="Processing ground truth assets"):
        if asset.filename not in image_name_map:
            image_name_map[asset.filename] = image_counter
            image_counter += 1

        image_id = image_name_map[asset.filename]
        images.append(
            {
                "id": image_id,
                "file_name": asset.filename,
                "width": asset.width,
                "height": asset.height,
            }
        )

        asset_annotations = extract_asset_annotations(asset, inference_type)
        for ann in asset_annotations:
            label_name = ann.label.name
            if label_name not in label_name_map:
                label_name_map[label_name] = label_counter
                categories.append({"id": label_counter, "name": label_name})
                label_counter += 1

            category_id = label_name_map[label_name]
            annotations.append(
                build_gt_annotation(
                    ann,
                    image_id,
                    label_name,
                    category_id,
                    annotation_id,
                    inference_type,
                )
            )
            annotation_id += 1

    return (
        {"images": images, "annotations": annotations, "categories": categories},
        image_name_map,
        label_name_map,
        categories,
    )


def create_coco_files_from_experiment(
    experiment: Experiment,
    assets: list[Asset] | MultiAsset,
    gt_coco_path: str,
    pred_coco_path: str,
    inference_type: InferenceType,
) -> None:
    evaluations = experiment.list_evaluations()
    image_name_map: dict[str, int] = {}
    label_name_map: dict[str, int] = {}
    categories: list[dict[str, str]] = []

    ground_truth_coco, image_name_map, label_name_map, categories = (
        generate_coco_ground_truth(
            assets, image_name_map, label_name_map, categories, inference_type
        )
    )
    save_json(ground_truth_coco, gt_coco_path)

    predictions_coco = generate_coco_predictions(
        evaluations,
        image_name_map,
        label_name_map,
        categories,
        gt_coco_path,
        inference_type,
    )
    save_json(predictions_coco, pred_coco_path)
