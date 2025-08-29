import numpy as np
import torch


def box_iou(box1, box2, eps=1e-7):
    """
    Calculate intersection-over-union (IoU) of boxes. Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Based on https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py.

    Args:
        box1 (torch.Tensor): A tensor of shape (N, 4) representing N bounding boxes.
        box2 (torch.Tensor): A tensor of shape (M, 4) representing M bounding boxes.
        eps (float, optional): A small value to avoid division by zero. Defaults to 1e-7.

    Returns:
        (torch.Tensor): An NxM tensor containing the pairwise IoU values for every element in box1 and box2.
    """
    # NOTE: Need .float() to get accurate iou values
    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = (
        box1.float().unsqueeze(1).chunk(2, 2),
        box2.float().unsqueeze(0).chunk(2, 2),
    )
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp_(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / ((a2 - a1).prod(2) + (b2 - b1).prod(2) - inter + eps)


def compute_full_confusion_matrix(
    gt_annotations: list[dict],
    pred_annotations: list[dict],
    label_map: dict[int, str],
    iou_threshold: float = 0.5,
) -> np.ndarray:
    """
    Compute a confusion matrix for object detection with a background class.

    Args:
        gt_annotations (List[dict]): Ground truth annotations from COCO GT (coco.loadAnns()).
        pred_annotations (List[dict]): Predicted annotations from COCO Pred (coco.loadAnns()).
        label_map (dict): Mapping of category indices (as int) to class names.
        iou_threshold (float): IoU threshold for matching.

    Returns:
        np.ndarray: Confusion matrix of shape (num_classes+1, num_classes+1)
                    where the last index represents 'background'.
    """
    label_name_to_index = {name: int(idx) for idx, name in label_map.items()}
    num_classes = len(label_name_to_index)
    confusion = np.zeros((num_classes + 1, num_classes + 1), dtype=int)

    gt_cat_id_to_index = _build_cat_id_to_index(gt_annotations)
    pred_cat_id_to_index = _build_cat_id_to_index(pred_annotations)

    gt_by_image = _organize_annotations_by_image(gt_annotations, gt_cat_id_to_index)
    pred_by_image = _organize_annotations_by_image(
        pred_annotations, pred_cat_id_to_index
    )

    for image_id in set(gt_by_image) | set(pred_by_image):
        gts = gt_by_image.get(image_id, [])
        preds = pred_by_image.get(image_id, [])
        _update_confusion_matrix_for_image(
            gts=gts,
            preds=preds,
            gt_cat_id_to_index=gt_cat_id_to_index,
            pred_cat_id_to_index=pred_cat_id_to_index,
            confusion=confusion,
            num_classes=num_classes,
            iou_threshold=iou_threshold,
        )

    return confusion


def _build_cat_id_to_index(annotations: list[dict]) -> dict[int, int]:
    mapping = {}
    for ann in annotations:
        cat_id = ann["category_id"]
        if cat_id not in mapping:
            mapping[cat_id] = cat_id
    return mapping


def _organize_annotations_by_image(
    annotations: list[dict], cat_id_to_index: dict[int, int]
) -> dict[str, list]:
    by_image: dict[str, list] = {}
    for ann in annotations:
        if ann["category_id"] in cat_id_to_index:
            by_image.setdefault(ann["image_id"], []).append(ann)
    return by_image


def _update_confusion_matrix_for_image(
    gts: list[dict],
    preds: list[dict],
    gt_cat_id_to_index: dict[int, int],
    pred_cat_id_to_index: dict[int, int],
    confusion: np.ndarray,
    num_classes: int,
    iou_threshold: float,
) -> None:
    gt_boxes = torch.tensor([g["bbox"] for g in gts]) if gts else torch.empty((0, 4))
    gt_labels = torch.tensor(
        [
            gt_cat_id_to_index[g["category_id"]]
            for g in gts
            if g["category_id"] in gt_cat_id_to_index
        ],
        dtype=torch.long,
    )

    pred_boxes = (
        torch.tensor([p["bbox"] for p in preds]) if preds else torch.empty((0, 4))
    )
    pred_labels = torch.tensor(
        [
            pred_cat_id_to_index[p["category_id"]]
            for p in preds
            if p["category_id"] in pred_cat_id_to_index
        ],
        dtype=torch.long,
    )

    matched_gt = set()

    if len(gt_boxes) and len(pred_boxes):
        # Convert to xyxy
        gt_boxes[:, 2:] += gt_boxes[:, :2]
        pred_boxes[:, 2:] += pred_boxes[:, :2]

        ious = box_iou(gt_boxes, pred_boxes)
        i, j = torch.where(ious > iou_threshold)

        matches = []
        for gt_idx, pred_idx in zip(i.tolist(), j.tolist()):
            if gt_idx not in matched_gt:
                confusion[pred_labels[pred_idx], gt_labels[gt_idx]] += 1
                matched_gt.add(gt_idx)
                matches.append(pred_idx)

        unmatched_preds = set(range(len(pred_boxes))) - set(matches)
        for idx in unmatched_preds:
            confusion[pred_labels[idx], num_classes] += 1
    else:
        for pred_label in pred_labels:
            confusion[pred_label, num_classes] += 1

    unmatched_gt = set(range(len(gt_boxes))) - matched_gt
    for idx in unmatched_gt:
        confusion[num_classes, gt_labels[idx]] += 1


def compute_confusion_matrix_impl(
    coco_gt, coco_pred, label_map, training_labelmap, experiment_logger
):
    gt_anns = coco_gt.loadAnns(coco_gt.getAnnIds())
    pred_anns = coco_pred.loadAnns(coco_pred.getAnnIds())

    conf_matrix = compute_full_confusion_matrix(
        gt_annotations=gt_anns,
        pred_annotations=pred_anns,
        label_map=label_map,
        iou_threshold=0.5,
    )

    label_map[len(label_map)] = "background"

    experiment_logger.log_confusion_matrix(
        name="confusion-matrix",
        labelmap=training_labelmap,
        matrix=conf_matrix,
        phase="test",
    )
