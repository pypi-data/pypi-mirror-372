import os
from typing import Any, Generic, TypeVar

from picsellia import Experiment

from picsellia_cv_engine.core.contexts import PicselliaContext
from picsellia_cv_engine.core.parameters import (
    AugmentationParameters,
    HyperParameters,
)
from picsellia_cv_engine.core.parameters.export_parameters import TExportParameters

THyperParameters = TypeVar("THyperParameters", bound=HyperParameters)
TAugmentationParameters = TypeVar(
    "TAugmentationParameters", bound=AugmentationParameters
)


class LocalTrainingContext(
    PicselliaContext, Generic[THyperParameters, TAugmentationParameters]
):
    """
    Local context for training pipelines without a real job on Picsellia.
    """

    def __init__(
        self,
        hyperparameters_cls: type[THyperParameters],
        augmentation_parameters_cls: type[TAugmentationParameters],
        export_parameters_cls: type[TExportParameters],
        api_token: str | None = None,
        host: str | None = None,
        organization_id: str | None = None,
        organization_name: str | None = None,
        experiment_id: str | None = None,
        working_dir: str | None = None,
    ):
        """
        Initialize the training context using an experiment and parameter classes.

        Raises:
            ValueError: If experiment ID is provided but the experiment cannot be found.
        """
        super().__init__(
            api_token=api_token,
            host=host,
            organization_id=organization_id,
            organization_name=organization_name,
            working_dir=working_dir,
        )

        self.experiment_id = experiment_id
        if self.experiment_id:
            self.experiment = self._initialize_experiment()

        parameters_log_data = self.experiment.get_log("parameters").data

        self.hyperparameters = hyperparameters_cls(log_data=parameters_log_data)
        self.augmentation_parameters = augmentation_parameters_cls(
            log_data=parameters_log_data
        )
        self.export_parameters = export_parameters_cls(log_data=parameters_log_data)

        self._working_dir_override = working_dir

    @property
    def working_dir(self) -> str:
        """Return the working directory path for the experiment."""
        if self._working_dir_override:
            return self._working_dir_override
        return os.path.join(os.getcwd(), self.experiment.name)

    def to_dict(self) -> dict[str, Any]:
        """Convert the context to a dictionary representation."""
        return {
            "context_parameters": {
                "host": self.host,
                "organization_id": self.organization_id,
                "organization_name": self.organization_name,
                "experiment_id": self.experiment_id,
            },
            "hyperparameters": self._process_parameters(
                parameters_dict=self.hyperparameters.to_dict(),
                defaulted_keys=self.hyperparameters.defaulted_keys,
            ),
            "augmentation_parameters": self._process_parameters(
                parameters_dict=self.augmentation_parameters.to_dict(),
                defaulted_keys=self.augmentation_parameters.defaulted_keys,
            ),
            "export_parameters": self._process_parameters(
                parameters_dict=self.export_parameters.to_dict(),
                defaulted_keys=self.export_parameters.defaulted_keys,
            ),
        }

    def _initialize_experiment(self) -> Experiment:
        """Fetch the experiment by ID from Picsellia."""
        return self.client.get_experiment_by_id(self.experiment_id)
