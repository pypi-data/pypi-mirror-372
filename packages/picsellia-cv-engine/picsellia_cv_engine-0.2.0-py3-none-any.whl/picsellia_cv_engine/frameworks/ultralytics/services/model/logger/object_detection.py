from picsellia import Experiment

from picsellia_cv_engine.core.services.model.logging import (
    BaseLogger,
    Metric,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.base import (
    UltralyticsBaseMetricMapping,
)


class UltralyticsObjectDetectionMetricMapping(UltralyticsBaseMetricMapping):
    """
    Defines the metric mapping for object detection tasks using the Ultralytics framework.

    This mapping class registers framework-specific metric names and their corresponding standard names
    for both training and validation phases. It includes loss components, label metrics, and evaluation metrics.
    """

    def __init__(self):
        """
        Initializes the object detection metric mapping.

        Sets up metric associations for box loss, classification loss, distribution focal loss (DFL),
        precision, recall, and mAP values.
        """
        super().__init__()
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="box_loss", framework_name="train/box_loss"),
        )
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="cls_loss", framework_name="train/cls_loss"),
        )
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="dfl_loss", framework_name="train/dfl_loss"),
        )
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="labels", framework_name="labels"),
        )
        self.add_metric(
            phase="train",
            metric=Metric(
                standard_name="labels_correlogram", framework_name="labels_correlogram"
            ),
        )

        self.add_metric(
            phase="val",
            metric=Metric(standard_name="box_loss", framework_name="val/box_loss"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(standard_name="cls_loss", framework_name="val/cls_loss"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(standard_name="dfl_loss", framework_name="val/dfl_loss"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="precision(B)", framework_name="metrics/precision(B)"
            ),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="recall(B)", framework_name="metrics/recall(B)"
            ),
        )
        self.add_metric(
            phase="val",
            metric=Metric(standard_name="mAP50(B)", framework_name="metrics/mAP50(B)"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="mAP50-95(B)", framework_name="metrics/mAP50-95(B)"
            ),
        )


class UltralyticsObjectDetectionLogger(BaseLogger):
    """
    Logger for Ultralytics-based object detection models.

    This logger uses an UltralyticsObjectDetectionMetricMapping to normalize metric names and
    logs them to a Picsellia experiment during training and validation phases.
    """

    def __init__(
        self,
        experiment: Experiment,
        metric_mapping: UltralyticsObjectDetectionMetricMapping,
    ):
        """
        Initializes the object detection logger with a given experiment and metric mapping.

        Args:
            experiment (Experiment): The experiment object used for logging.
            metric_mapping (UltralyticsObjectDetectionMetricMapping): Mapping for translating framework-specific metrics.
        """
        super().__init__(experiment=experiment, metric_mapping=metric_mapping)
