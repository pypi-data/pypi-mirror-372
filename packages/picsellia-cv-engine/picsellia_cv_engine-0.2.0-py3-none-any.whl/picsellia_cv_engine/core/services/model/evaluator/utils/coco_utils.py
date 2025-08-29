import json
import logging

from picsellia.types.enums import InferenceType
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval


def load_json(file_path: str) -> dict:
    """
    Load and return the contents of a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    with open(file_path) as f:
        return json.load(f)


def save_json(data: dict, file_path: str):
    """
    Save data to a JSON file with an indentation of 4 spaces.

    Args:
        data (dict): Data to save.
        file_path (str): Output path for the JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def adjust_image_ids(coco_data: dict):
    """
    Adjust image IDs in COCO data. If the image IDs start at 0, they are incremented by 1.

    Args:
        coco_data (dict): COCO data containing the "images" and "annotations" keys.
    """
    image_ids = [img["id"] for img in coco_data["images"]]
    if image_ids and min(image_ids) == 0:
        id_mapping = {old_id: old_id + 1 for old_id in image_ids}
        for img in coco_data["images"]:
            img["id"] = id_mapping[img["id"]]
        for ann in coco_data["annotations"]:
            ann["image_id"] = id_mapping.get(ann["image_id"], ann["image_id"])


def renumber_annotation_ids(coco_data: dict):
    """
    Renumber annotation IDs sequentially starting from 1.

    Args:
        coco_data (dict): COCO data containing the "annotations" key.
    """
    for i, ann in enumerate(coco_data["annotations"], start=1):
        ann["id"] = i


def fix_coco_ids(coco_path: str) -> str:
    """
    Fix image and annotation IDs in a COCO file. Images whose IDs start at 0 are adjusted and
    annotation IDs are renumbered sequentially. The fixed file is saved with the suffix '_fixed'.

    Args:
        coco_path (str): Path to the original COCO file.

    Returns:
        str: Path to the fixed COCO file.
    """
    coco_data = load_json(coco_path)
    adjust_image_ids(coco_data)
    renumber_annotation_ids(coco_data)
    fixed_path = coco_path.replace(".json", "_fixed.json")
    save_json(coco_data, fixed_path)
    return fixed_path


def create_image_id_mapping(gt_images: list[dict], pred_images: list[dict]) -> dict:
    """
    Create a mapping between image IDs from the ground truth and prediction data based on the 'file_name' field.

    Args:
        gt_images (list): List of ground truth images (each a dict with 'file_name' and 'id').
        pred_images (list): List of predicted images (each a dict with 'file_name' and 'id').

    Returns:
        dict: Mapping {predicted_image_id: ground_truth_image_id}.
    """
    gt_id_map = {img["file_name"]: img["id"] for img in gt_images}
    pred_id_map = {img["file_name"]: img["id"] for img in pred_images}
    mapping = {}
    for file_name, pred_id in pred_id_map.items():
        if file_name in gt_id_map:
            mapping[pred_id] = gt_id_map[file_name]
    return mapping


def fix_image_ids(pred_data: dict, id_mapping: dict):
    """
    Fix the 'image_id' fields in prediction data using the provided mapping.

    Args:
        pred_data (dict): Prediction COCO data containing "images" and "annotations".
        id_mapping (dict): Mapping between predicted and ground truth image IDs.
    """
    for img in pred_data["images"]:
        if img["id"] in id_mapping:
            img["id"] = id_mapping[img["id"]]
    for ann in pred_data["annotations"]:
        if ann["image_id"] in id_mapping:
            ann["image_id"] = id_mapping[ann["image_id"]]


def match_image_ids(
    ground_truth_file: str, prediction_file: str, corrected_prediction_file: str
) -> None:
    """
    Match image IDs between the ground truth and prediction files.
    Loads the ground truth and prediction JSON files, creates a mapping based on 'file_name',
    fixes the prediction image IDs using the mapping, and saves the corrected predictions.

    Args:
        ground_truth_file (str): Path to the COCO ground truth file.
        prediction_file (str): Path to the COCO predictions file.
        corrected_prediction_file (str): Output path for the corrected predictions file.
    """
    gt_data = load_json(file_path=ground_truth_file)
    pred_data = load_json(file_path=prediction_file)
    id_mapping = create_image_id_mapping(
        gt_images=gt_data.get("images", []), pred_images=pred_data.get("images", [])
    )
    if not id_mapping:
        logging.warning(
            "No mapping found. Please check that the file names in the ground truth and predictions match!"
        )
        return
    logging.info(f"{len(id_mapping)} mappings found. Correcting prediction IDs...")
    fix_image_ids(pred_data=pred_data, id_mapping=id_mapping)
    save_json(data=pred_data, file_path=corrected_prediction_file)
    logging.info(f"Corrected file saved as: {corrected_prediction_file}")


def compute_tp_fp_fn(coco_eval: COCOeval) -> dict:
    """
    Compute the number of True Positives (TP), False Positives (FP), and False Negatives (FN) per category
    using a COCOeval object.

    Args:
        coco_eval (COCOeval): COCOeval object after evaluation.

    Returns:
        dict: Dictionary mapping each category ID to a dict with keys "TP", "FP", and "FN".
    """
    eval_imgs = coco_eval.evalImgs
    category_ids = coco_eval.params.catIds
    metrics = {cat_id: {"TP": 0, "FP": 0, "FN": 0} for cat_id in category_ids}

    for img_res in eval_imgs:
        if img_res is None or img_res["aRng"] != [0, 10000000000.0]:
            continue

        cat_id = img_res["category_id"]
        if cat_id not in category_ids:
            continue

        detection_ignore = img_res["dtIgnore"][0]
        gt_ignore = img_res["gtIgnore"].astype(int).sum()
        mask = ~detection_ignore

        tp = (img_res["dtMatches"][0][mask] > 0).sum()
        fp = (img_res["dtMatches"][0][mask] == 0).sum()
        n_gt = len(img_res["gtIds"]) - gt_ignore
        fn = max(n_gt - tp, 0)

        metrics[cat_id]["TP"] += tp
        metrics[cat_id]["FP"] += fp
        metrics[cat_id]["FN"] += fn

    return metrics


def calculate_metrics(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    """
    Calculate precision, recall, and F1-score.

    Args:
        tp (int): Number of True Positives.
        fp (int): Number of False Positives.
        fn (int): Number of False Negatives.

    Returns:
        tuple: Precision, recall, and F1-score.
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = (
        (2 * precision * recall / (precision + recall))
        if (precision + recall) > 0
        else 0
    )
    return precision, recall, f1_score


def evaluate_category(
    coco_gt: COCO,
    coco_pred: COCO,
    cat_name: str,
    inference_type: InferenceType,
) -> dict:
    """
    Evaluate predictions for a given category using COCO metrics.
    Runs evaluation for the specified category and area 'all', then computes additional metrics
    (TP, FP, FN, precision, recall, F1-score).

    Args:
        coco_gt (COCO): COCO object for the ground truth.
        coco_pred (COCO): COCO object for the predictions.
        cat_name (str): Category name.
        inference_type (InferenceType): Type of inference (classification, detection, or segmentation).

    Returns:
        dict: Dictionary containing evaluation metrics for the category.
    """
    iouType = "bbox" if inference_type == InferenceType.OBJECT_DETECTION else "segm"
    coco_eval = COCOeval(cocoGt=coco_gt, cocoDt=coco_pred, iouType=iouType)
    cat_ids = coco_gt.getCatIds(catNms=[cat_name])

    if not cat_ids:
        return {
            "Class": cat_name,
            "Images": 0,
            "Instances": 0,
            "Box(P)": 0,
            "Box(R)": 0,
            "Box(mAP50)": 0,
            "Box(mAP50-95)": 0,
            "Box(mAR50-95)": 0,
        }

    cat_id = cat_ids[0]
    coco_eval.params.catIds = [cat_id]
    coco_eval.params.catIds = [cat_id]
    # coco_eval.params.iouThrs = [0.5]
    coco_eval.params.areaRng = [[0, 10000000000.0]]
    coco_eval.params.areaRngLbl = ["all"]

    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()

    stats = coco_eval.stats.tolist()
    detection_metrics = compute_tp_fp_fn(coco_eval)
    tp = detection_metrics[cat_id]["TP"]
    fp = detection_metrics[cat_id]["FP"]
    fn = detection_metrics[cat_id]["FN"]
    precision, recall, f1_score = calculate_metrics(tp=tp, fp=fp, fn=fn)

    num_images = len(coco_gt.getImgIds(catIds=[cat_id]))
    num_instances = tp + fn

    if iouType == "bbox":
        return {
            "Class": cat_name,
            "Images": num_images,
            "Instances": num_instances,
            "Box(P)": precision,
            "Box(R)": recall,
            "Box(mAP50)": stats[1],
            "Box(mAP50-95)": stats[0],
            "Box(mAR50-95)": stats[8],
        }
    else:
        return {
            "Class": cat_name,
            "Images": num_images,
            "Instances": num_instances,
            "Mask(P)": precision,
            "Mask(R)": recall,
            "Mask(mAP50)": stats[1],
            "Mask(mAP50-95)": stats[0],
            "Mask(mAR50-95)": stats[8],
        }
