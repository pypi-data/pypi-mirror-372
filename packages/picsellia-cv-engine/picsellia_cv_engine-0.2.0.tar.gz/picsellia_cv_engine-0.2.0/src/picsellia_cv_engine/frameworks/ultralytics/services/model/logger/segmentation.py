from picsellia import Experiment

from picsellia_cv_engine.core.services.model.logging import (
    BaseLogger,
    Metric,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.object_detection import (
    UltralyticsObjectDetectionMetricMapping,
)


class UltralyticsSegmentationMetricMapping(UltralyticsObjectDetectionMetricMapping):
    """
    Defines the metric mapping for segmentation tasks using the Ultralytics framework.

    This class extends the object detection mapping and adds segmentation-specific metrics,
    such as segmentation loss and mask-based precision, recall, and mAP.
    """

    def __init__(self):
        """
        Initializes the segmentation-specific metric mapping.

        Adds metrics for training and validation segmentation loss, as well as mask precision,
        recall, mAP50, and mAP50-95.
        """
        super().__init__()
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="seg_loss", framework_name="train/seg_loss"),
        )

        self.add_metric(
            phase="val",
            metric=Metric(standard_name="seg_loss", framework_name="val/seg_loss"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="precision(M)", framework_name="metrics/precision(M)"
            ),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="recall(M)", framework_name="metrics/recall(M)"
            ),
        )
        self.add_metric(
            phase="val",
            metric=Metric(standard_name="mAP50(M)", framework_name="metrics/mAP50(M)"),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="mAP50-95(M)", framework_name="metrics/mAP50-95(M)"
            ),
        )


class UltralyticsSegmentationLogger(BaseLogger):
    """
    Logger for Ultralytics-based segmentation models.

    This logger uses an UltralyticsSegmentationMetricMapping to log metrics
    during training and validation phases to a Picsellia experiment.
    """

    def __init__(
        self,
        experiment: Experiment,
        metric_mapping: UltralyticsSegmentationMetricMapping,
    ):
        """
        Initializes the segmentation logger with the given experiment and metric mapping.

        Args:
            experiment (Experiment): The experiment used for logging.
            metric_mapping (UltralyticsSegmentationMetricMapping): The segmentation-specific metric mapping.
        """
        super().__init__(experiment=experiment, metric_mapping=metric_mapping)
