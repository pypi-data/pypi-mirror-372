from enum import Enum, auto


class StepState(Enum):
    """
    Enumeration representing the various states a step in a pipeline can be in.

    Attributes:
        PENDING: The step is defined but has not started yet.
        RUNNING: The step is currently executing.
        SUCCESS: The step completed successfully.
        FAILED: The step encountered an error and did not complete.
        SKIPPED: The step was intentionally skipped.
    """

    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()


class PipelineState(Enum):
    """
    Enumeration representing the overall execution state of a pipeline.

    Attributes:
        PENDING: The pipeline has not started yet.
        RUNNING: The pipeline is currently executing.
        SUCCESS: The pipeline completed all steps successfully.
        FAILED: The pipeline encountered an unrecoverable error and stopped.
        PARTIAL_SUCCESS: Some steps completed successfully, while others failed or were skipped.
    """

    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    PARTIAL_SUCCESS = auto()


class DatasetSplitName(Enum):
    """
    Enumeration of standard dataset split names for machine learning workflows.

    Defines the conventional dataset partitions used during model development:

    Attributes:
        TRAIN (str): Dataset used to train the model.
        VAL (str): Dataset used to validate and tune the model during training.
        TEST (str): Dataset used to evaluate model performance after training.
    """

    TRAIN = "train"
    VAL = "val"
    TEST = "test"
