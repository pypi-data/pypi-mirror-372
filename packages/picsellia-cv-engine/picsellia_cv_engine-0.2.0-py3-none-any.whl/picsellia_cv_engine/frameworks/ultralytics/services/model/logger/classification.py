from picsellia import Experiment

from picsellia_cv_engine.core.services.model.logging import (
    BaseLogger,
    Metric,
)
from picsellia_cv_engine.core.services.model.logging.classification_logger import (
    ClassificationMetricMapping,
)
from picsellia_cv_engine.frameworks.ultralytics.services.model.logger.base import (
    UltralyticsBaseMetricMapping,
)


class UltralyticsClassificationMetricMapping(UltralyticsBaseMetricMapping):
    """
    Defines the metric mapping for classification tasks in the Ultralytics framework.

    This class extends the base Ultralytics metric mapping and adds classification-specific metrics
    such as top-1 and top-5 accuracy and loss for both training and validation phases.
    """

    def __init__(self):
        """
        Initializes the Ultralytics-specific classification metric mapping.

        Registers classification metrics including loss, top-1 accuracy, and top-5 accuracy
        for both training and validation.
        """
        super().__init__()
        self.add_metric(
            phase="train",
            metric=Metric(standard_name="loss", framework_name="train/loss"),
        )

        self.add_metric(
            phase="train",
            metric=Metric(
                standard_name="accuracy", framework_name="metrics/accuracy_top1"
            ),
        )
        self.add_metric(
            phase="train",
            metric=Metric(
                standard_name="accuracy_top5", framework_name="metrics/accuracy_top5"
            ),
        )

        self.add_metric(
            phase="val", metric=Metric(standard_name="loss", framework_name="val/loss")
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="accuracy", framework_name="metrics/accuracy_top1"
            ),
        )
        self.add_metric(
            phase="val",
            metric=Metric(
                standard_name="accuracy_top5", framework_name="metrics/accuracy_top5"
            ),
        )


class UltralyticsClassificationLogger(BaseLogger):
    """
    Logger for Ultralytics-based classification models.

    This class is responsible for logging classification-related metrics during training
    and validation, using an Ultralytics-compatible metric mapping.
    """

    def __init__(
        self, experiment: Experiment, metric_mapping: ClassificationMetricMapping
    ):
        """
        Initialize the UltralyticsClassificationLogger with an experiment and a metric mapping.

        Args:
            experiment (Experiment): The experiment object used for logging.
            metric_mapping (ClassificationMetricMapping): The metric mapping used to normalize metric names.
        """
        super().__init__(experiment=experiment, metric_mapping=metric_mapping)
