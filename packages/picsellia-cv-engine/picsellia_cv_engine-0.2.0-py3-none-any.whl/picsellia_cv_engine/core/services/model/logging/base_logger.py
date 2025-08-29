import logging
import math

import numpy as np
from picsellia import Experiment
from picsellia.types.enums import LogType

logger = logging.getLogger(__name__)


class Metric:
    """
    Represents a metric with a standard and optional framework-specific name.

    Attributes:
        standard_name (str): Canonical name used internally.
        framework_name (str | None): Optional name used by a specific framework.
    """

    def __init__(self, standard_name: str, framework_name: str | None = None):
        """
        Initializes a Metric object.

        Args:
            standard_name (str): The standard name of the metric.
            framework_name (Optional[str]): The framework-specific name of the metric (optional).
        """
        self.standard_name = standard_name
        self.framework_name = framework_name

    def get_name(self) -> str:
        """
        Get the standard name of the metric.

        Returns:
            str: Standard metric name.
        """
        return self.standard_name


class MetricMapping:
    """
    Holds mappings between framework-specific metric names and standard names.

    Supports phases: 'train', 'val', 'test'.
    """

    def __init__(self):
        """
        Initializes a MetricMapping object with empty lists for train, validation, and test phases.
        """
        self.mappings: dict[str, list[Metric]] = {
            "train": [],
            "val": [],
            "test": [],
        }

    def add_metric(self, phase: str, metric: Metric) -> None:
        """
        Add a metric to the specified phase.

        Args:
            phase (str): One of 'train', 'val', or 'test'.
            metric (Metric): The metric to register.

        Raises:
            ValueError: If phase is unknown.
        """
        if phase in self.mappings:
            self.mappings[phase].append(metric)
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def get_mapping(self, phase: str | None = None) -> dict[str, str]:
        """
        Get mapping of framework names to standard names for a given phase.

        Args:
            phase (str | None): One of 'train', 'val', 'test'.

        Returns:
            dict: Mapping of metric names.
        """
        if phase is None:
            return {}
        return {
            metric.framework_name or metric.standard_name: metric.standard_name
            for metric in self.mappings.get(phase, [])
        }


class BaseLogger:
    """
    Generic logger for logging metrics, values, images, confusion matrices and tables.
    """

    def __init__(self, experiment: Experiment, metric_mapping: MetricMapping):
        """
        Initializes the BaseLogger with an experiment and a metric mapping.

        Args:
            experiment (Experiment): The experiment object for logging.
            metric_mapping (MetricMapping): The metric mapping object to translate metric names.
        """
        self.experiment = experiment
        self.metric_mapping = metric_mapping

    def log_metric(
        self,
        name: str,
        value: float,
        log_type: LogType = LogType.LINE,
        phase: str | None = None,
    ):
        """
        Log a metric value (e.g. for line plot).

        Args:
            name (str): Metric name.
            value (float): Metric value.
            log_type (LogType): Logging type (default LINE).
            phase (str | None): Phase name.
        """
        log_name = self.get_log_name(metric_name=name, phase=phase)
        sanitized_value = Sanitizer.sanitize_value(value)
        if sanitized_value:
            self.experiment.log(log_name, value, log_type)
        else:
            logger.info(
                f"Value {value} is not loggable. Skipping logging for {log_name}."
            )

    def log_value(
        self, name: str, value: float, phase: str | None = None, precision: int = 4
    ):
        """
        Log a scalar value (e.g., accuracy score).

        Args:
            name (str): Metric name.
            value (float): Value to log.
            phase (str | None): Phase name.
            precision (int): Decimal precision to round.
        """
        log_name = self.get_log_name(metric_name=name, phase=phase)
        sanitized_value = Sanitizer.sanitize_value(round(value, precision))
        if sanitized_value:
            self.experiment.log(log_name, sanitized_value, LogType.VALUE)
        else:
            logger.info(
                f"Value {value} is not loggable. Skipping logging for {log_name}."
            )

    def log_image(self, name: str, image_path: str, phase: str | None = None):
        """
        Log an image file.

        Args:
            name (str): Log name.
            image_path (str): Path to image.
            phase (str | None): Phase name.
        """
        log_name = self.get_log_name(metric_name=name, phase=phase)
        self.experiment.log(log_name, image_path, LogType.IMAGE)

    def log_confusion_matrix(
        self, name: str, labelmap: dict, matrix: np.ndarray, phase: str | None = None
    ):
        """
        Log a confusion matrix as a heatmap.

        Args:
            name (str): Log name.
            labelmap (dict): Mapping of label indices to names.
            matrix (np.ndarray): Confusion matrix.
            phase (str | None): Phase name.
        """
        log_name = self.get_log_name(metric_name=name, phase=phase)
        sanitized_confusion = Sanitizer.sanitize_confusion_matrix(
            list(labelmap.values()), matrix
        )
        self.experiment.log(log_name, sanitized_confusion, LogType.HEATMAP)

    def _format_confusion_matrix(self, labelmap: dict, matrix: np.ndarray) -> dict:
        """
        Internal formatter for confusion matrix (unused).

        Args:
            labelmap (dict): Index-to-name mapping.
            matrix (np.ndarray): Raw matrix.

        Returns:
            dict: Formatted structure.
        """
        return {"categories": list(labelmap.values()), "values": matrix.tolist()}

    def log_table(self, name: str, data: dict, phase: str | None = None):
        """
        Log a table (either a key-value dict or 2D matrix).

        Args:
            name (str): Log name.
            data (dict): Data to log.
            phase (str | None): Phase name.

        Raises:
            ValueError: If matrix structure is inconsistent.
        """
        log_name = self.get_log_name(metric_name=name, phase=phase)

        if all(k in data for k in ["data", "rows", "columns"]):
            matrix = data["data"]
            rows = data["rows"]
            columns = data["columns"]

            if len(matrix) != len(rows):
                raise ValueError(f"Row count mismatch: {len(rows)} vs {len(matrix)}")
            if any(len(row) != len(columns) for row in matrix):
                raise ValueError("Column count mismatch.")

            sanitized_data = {
                "data": Sanitizer.sanitize_matrix(matrix),
                "rows": rows,
                "columns": columns,
            }
        else:
            sanitized_data = Sanitizer.sanitize_dict(data)

        self.experiment.log(name=log_name, data=sanitized_data, type=LogType.TABLE)

    def get_log_name(self, metric_name: str, phase: str | None = None) -> str:
        """
        Construct log name with optional phase and mapped name.

        Args:
            metric_name (str): Base metric name.
            phase (str | None): Optional phase.

        Returns:
            str: Full log name.
        """
        mapped_name = self.metric_mapping.get_mapping(phase).get(
            metric_name, metric_name
        )
        return f"{phase}/{mapped_name}" if phase else mapped_name


class Sanitizer:
    """
    Utility class to convert values and structures into loggable formats.
    """

    @staticmethod
    def sanitize_value(value):
        """
        Convert single value to loggable primitive.

        Args:
            value: Value to convert.

        Returns:
            int | float | str: Clean value.
        """
        # Convert NumPy types to native Python types
        if isinstance(value, (np.integer, np.floating)):
            value = value.item()

        # Handle floats and ints (including NaN or inf)
        if isinstance(value, (float, int)):
            if math.isnan(value) or math.isinf(value):
                return None
            return value

        # Strings are safe
        if isinstance(value, str):
            return value

        # Fallback for unsupported types
        return str(value)

    @classmethod
    def sanitize_dict(cls, data: dict) -> dict:
        """
        Sanitize values in a dict.

        Args:
            data (dict): Dictionary to sanitize.

        Returns:
            dict: Cleaned dictionary.
        """
        return {k: cls.sanitize_value(v) for k, v in data.items()}

    @classmethod
    def sanitize_matrix(cls, matrix: list[list]) -> list[list]:
        """
        Sanitize a matrix of values.

        Args:
            matrix (list[list]): 2D list.

        Returns:
            list[list]: Clean matrix.
        """
        return [[cls.sanitize_value(v) for v in row] for row in matrix]

    @classmethod
    def sanitize_confusion_matrix(cls, categories: list, matrix: np.ndarray) -> dict:
        """
        Format confusion matrix for logging.

        Args:
            categories (list): Category labels.
            matrix (np.ndarray): Matrix values.

        Returns:
            dict: Loggable structure.
        """
        return {
            "categories": list(categories),
            "values": cls.sanitize_matrix(matrix.tolist()),
        }
