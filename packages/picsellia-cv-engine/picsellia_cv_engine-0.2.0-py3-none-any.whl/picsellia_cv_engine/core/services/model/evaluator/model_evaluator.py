import logging
import os

import numpy as np
import pandas as pd
from picsellia import Experiment
from picsellia.sdk.asset import Asset, MultiAsset
from picsellia.types.enums import AddEvaluationType, InferenceType
from pycocotools.coco import COCO
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from picsellia_cv_engine.core.models import (
    PicselliaClassificationPrediction,
    PicselliaOCRPrediction,
    PicselliaPolygonPrediction,
    PicselliaRectanglePrediction,
)
from picsellia_cv_engine.core.services.model.evaluator.utils.coco_converter import (
    create_coco_files_from_experiment,
)
from picsellia_cv_engine.core.services.model.evaluator.utils.coco_utils import (
    evaluate_category,
    fix_coco_ids,
    match_image_ids,
)
from picsellia_cv_engine.core.services.model.logging import BaseLogger, MetricMapping

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluates model predictions and logs metrics into a Picsellia experiment.

    Supports classification, detection (rectangle), OCR, and segmentation (polygon) evaluations,
    including COCO-style and sklearn metrics.
    """

    def __init__(self, experiment: Experiment, inference_type: InferenceType) -> None:
        """
        Initialize the evaluator with a Picsellia experiment.

        Args:
            experiment (Experiment): The experiment where results will be logged.
            inference_type (InferenceType): Type of inference (classification, detection, etc.).
        """
        self.experiment = experiment
        self.inference_type = inference_type
        self.experiment_logger = BaseLogger(
            experiment=experiment, metric_mapping=MetricMapping()
        )

    def evaluate(
        self,
        picsellia_predictions: (
            list[PicselliaClassificationPrediction]
            | list[PicselliaRectanglePrediction]
            | list[PicselliaPolygonPrediction]
            | list[PicselliaOCRPrediction]
        ),
    ) -> None:
        """
        Add and compute evaluation metrics from a list of predictions.

        Args:
            picsellia_predictions (list): List of PicselliaPrediction objects.
        """
        for prediction in picsellia_predictions:
            self.add_evaluation(prediction)
        self.experiment.compute_evaluations_metrics(inference_type=self.inference_type)

    def add_evaluation(
        self,
        evaluation: (
            PicselliaClassificationPrediction
            | PicselliaRectanglePrediction
            | PicselliaPolygonPrediction
            | PicselliaOCRPrediction
        ),
    ) -> None:
        """
        Add a single prediction to the experiment as evaluation.

        Args:
            evaluation: A prediction (classification, rectangle, OCR, or polygon).

        Raises:
            TypeError: If the prediction type is unsupported.
        """
        asset = evaluation.asset

        if isinstance(evaluation, PicselliaOCRPrediction):
            rectangles = [
                (
                    rectangle.value[0],
                    rectangle.value[1],
                    rectangle.value[2],
                    rectangle.value[3],
                    label.value,
                    conf.value,
                )
                for rectangle, label, conf in zip(
                    evaluation.boxes,
                    evaluation.labels,
                    evaluation.confidences,
                    strict=False,
                )
            ]
            rectangles_with_text = [
                (
                    rectangle.value[0],
                    rectangle.value[1],
                    rectangle.value[2],
                    rectangle.value[3],
                    label.value,
                    conf.value,
                    text.value,
                )
                for rectangle, label, conf, text in zip(
                    evaluation.boxes,
                    evaluation.labels,
                    evaluation.confidences,
                    evaluation.texts,
                    strict=False,
                )
            ]
            logger.info(
                f"Adding evaluation for asset {asset.filename} with rectangles {rectangles_with_text}"
            )
            self.experiment.add_evaluation(
                asset, add_type=AddEvaluationType.REPLACE, rectangles=rectangles
            )

        elif isinstance(evaluation, PicselliaRectanglePrediction):
            rectangles = [
                (
                    rectangle.value[0],
                    rectangle.value[1],
                    rectangle.value[2],
                    rectangle.value[3],
                    label.value,
                    conf.value,
                )
                for rectangle, label, conf in zip(
                    evaluation.boxes,
                    evaluation.labels,
                    evaluation.confidences,
                    strict=False,
                )
            ]
            logger.info(
                f"Adding evaluation for asset {asset.filename} with rectangles {rectangles}"
            )
            self.experiment.add_evaluation(
                asset, add_type=AddEvaluationType.REPLACE, rectangles=rectangles
            )

        elif isinstance(evaluation, PicselliaClassificationPrediction):
            classifications = [(evaluation.label.value, evaluation.confidence.value)]
            self.experiment.add_evaluation(
                asset,
                add_type=AddEvaluationType.REPLACE,
                classifications=classifications,
            )

        elif isinstance(evaluation, PicselliaPolygonPrediction):
            polygons = [
                (polygon.value, label.value, conf.value)
                for polygon, label, conf in zip(
                    evaluation.polygons,
                    evaluation.labels,
                    evaluation.confidences,
                    strict=False,
                )
            ]
            if not polygons:
                logger.info(
                    f"Adding an empty evaluation for asset {asset.filename} (no polygons found)."
                )
                self.experiment.add_evaluation(
                    asset, add_type=AddEvaluationType.REPLACE, polygons=[]
                )
            else:
                logger.info(
                    f"Adding evaluation for asset {asset.filename} with polygons {polygons}"
                )
                self.experiment.add_evaluation(
                    asset, add_type=AddEvaluationType.REPLACE, polygons=polygons
                )

        else:
            raise TypeError("Unsupported prediction type")

    def compute_coco_metrics(
        self,
        assets: list[Asset] | MultiAsset,
        output_dir: str,
        training_labelmap: dict[str, str],
    ) -> None:
        """
        Compute COCO metrics and log them into the experiment.

        Args:
            assets (list | MultiAsset): Assets to evaluate.
            output_dir (str): Directory to save metrics.
            training_labelmap (dict): Label ID-to-name mapping.
        """

        os.makedirs(output_dir, exist_ok=True)
        gt_coco_path = os.path.join(output_dir, "gt.json")
        pred_coco_path = os.path.join(output_dir, "pred.json")
        output_path = os.path.join(output_dir, "output.csv")

        label_map = {int(k): v for k, v in training_labelmap.items()}

        create_coco_files_from_experiment(
            experiment=self.experiment,
            assets=assets,
            gt_coco_path=gt_coco_path,
            pred_coco_path=pred_coco_path,
            inference_type=self.inference_type,
        )

        gt_path_fixed = fix_coco_ids(gt_coco_path)
        pred_path_fixed = fix_coco_ids(pred_coco_path)
        matched_prediction_file = pred_path_fixed.replace(".json", "_matched.json")
        match_image_ids(gt_path_fixed, pred_path_fixed, matched_prediction_file)
        coco_gt = COCO(gt_path_fixed)
        coco_pred = COCO(matched_prediction_file)

        results = [
            evaluate_category(
                coco_gt=coco_gt,
                coco_pred=coco_pred,
                cat_name=cat_name,
                inference_type=self.inference_type,
            )
            for cat_name in label_map.values()
        ]
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)
        logger.info(f"Results saved to: {output_path}")

        df = pd.read_csv(output_path).round(3)

        if not df.empty:
            row_labels = df["Class"].tolist()
            columns = df.columns.drop("Class").tolist()
            matrix = df.drop(columns=["Class"]).values.tolist()

            self.experiment_logger.log_table(
                name="metrics",
                data={"data": matrix, "rows": row_labels, "columns": columns},
                phase="test",
            )

            key_name_map = {
                "Box(mAP50)": "mAP50(B)",
                "Box(mAP50-95)": "mAP50-95(B)",
                "Box(mAR50-95)": "mAR50-95(B)",
                "Mask(mAP50)": "mAP50(M)",
                "Mask(mAP50-95)": "mAP50-95(M)",
                "Mask(mAR50-95)": "mAR50-95(M)",
            }

            for original_key, log_name in key_name_map.items():
                if original_key in df.columns:
                    mean_value = df[original_key].mean()
                    self.experiment_logger.log_value(
                        name=log_name, value=round(mean_value, 3), phase="test"
                    )

    def compute_classification_metrics(
        self,
        assets: list[Asset] | MultiAsset,
        output_dir: str,
        training_labelmap: dict[str, str],
    ) -> None:
        """
        Compute sklearn classification metrics (acc, precision, recall, F1).

        Args:
            assets (list | MultiAsset): Assets to evaluate.
            output_dir (str): Output directory.
            training_labelmap (dict): Label ID-to-name mapping.
        """
        os.makedirs(output_dir, exist_ok=True)
        gt_coco_path = os.path.join(output_dir, "gt.json")
        pred_coco_path = os.path.join(output_dir, "pred.json")

        create_coco_files_from_experiment(
            experiment=self.experiment,
            assets=assets,
            gt_coco_path=gt_coco_path,
            pred_coco_path=pred_coco_path,
            inference_type=self.inference_type,
        )

        gt_path_fixed = fix_coco_ids(gt_coco_path)
        pred_path_fixed = fix_coco_ids(pred_coco_path)
        matched_pred_path = pred_path_fixed.replace(".json", "_matched.json")
        match_image_ids(gt_path_fixed, pred_path_fixed, matched_pred_path)

        coco_gt = COCO(gt_path_fixed)
        coco_pred = COCO(matched_pred_path)

        gt_anns = coco_gt.loadAnns(coco_gt.getAnnIds())
        pred_anns = coco_pred.loadAnns(coco_pred.getAnnIds())

        y_true, y_pred = self._extract_classification_labels(
            gt_anns, pred_anns, training_labelmap
        )

        if not y_true.size:
            logger.warning("No matching ground truth and predictions found.")
            return

        metrics = self._compute_classification_scores(y_true, y_pred)

        logger.info(
            f"[Classification] Accuracy={metrics['accuracy']:.3f} | "
            f"Precision={metrics['precision']:.3f} | Recall={metrics['recall']:.3f} | F1={metrics['f1-score']:.3f}"
        )

        label_indices = sorted(int(i) for i in training_labelmap.keys())

        class_report = classification_report(
            y_true,
            y_pred,
            labels=label_indices,
            target_names=[training_labelmap[str(i)] for i in label_indices],
            output_dict=True,
            zero_division=0,
        )

        cm, label_map = self._compute_classification_confusion_matrix(
            y_true, y_pred, label_indices, training_labelmap
        )

        self.experiment_logger.log_confusion_matrix(
            name="confusion-matrix", labelmap=label_map, matrix=cm, phase="test"
        )

        rows, row_labels = [], []
        for class_name, metric in class_report.items():
            if class_name in ["accuracy", "macro avg", "weighted avg"]:
                continue
            row_labels.append(class_name)
            rows.append(
                [
                    round(metric["precision"], 3),
                    round(metric["recall"], 3),
                    round(metric["f1-score"], 3),
                ]
            )

        self.experiment_logger.log_table(
            name="metrics",
            data={
                "data": rows,
                "rows": row_labels,
                "columns": ["Precision", "Recall", "F1-score"],
            },
            phase="test",
        )

        for metric_name, metric_value in metrics.items():
            self.experiment_logger.log_value(
                name=metric_name, value=metric_value, phase="test"
            )

    def _extract_classification_labels(
        self, gt_anns, pred_anns, training_labelmap: dict[str, str]
    ):
        label_name_to_index = {v: int(k) for k, v in training_labelmap.items()}
        id_to_index = {}

        for cat in gt_anns:  # Use COCO category names
            if cat["name"] in label_name_to_index:
                id_to_index[cat["id"]] = label_name_to_index[cat["name"]]

        y_true = []
        y_pred = []

        image_to_gt = {}
        for ann in gt_anns:
            if ann["category_id"] in id_to_index:
                image_to_gt[ann["image_id"]] = id_to_index[ann["category_id"]]

        for ann in pred_anns:
            img_id = ann["image_id"]
            if img_id in image_to_gt and ann["category_id"] in id_to_index:
                y_true.append(image_to_gt[img_id])
                y_pred.append(id_to_index[ann["category_id"]])

        return np.array(y_true), np.array(y_pred)

    def _compute_classification_scores(self, y_true, y_pred):
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
        recall = recall_score(y_true, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

        return {
            "accuracy": round(accuracy, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1-score": round(f1, 3),
        }

    def _compute_classification_confusion_matrix(
        self, y_true, y_pred, label_indices, training_labelmap
    ):
        cm = confusion_matrix(y_true, y_pred, labels=label_indices)
        label_map = {i: training_labelmap[str(i)] for i in label_indices}
        return cm, label_map
