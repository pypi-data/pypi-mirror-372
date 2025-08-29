import os
from typing import Any, Generic, TypeVar

from picsellia import DatasetVersion, ModelVersion
from picsellia.types.enums import ProcessingType

from picsellia_cv_engine.core.contexts import (
    PicselliaContext,
)
from picsellia_cv_engine.core.parameters import Parameters

TParameters = TypeVar("TParameters", bound=Parameters)


class LocalDatasetProcessingContext(PicselliaContext, Generic[TParameters]):
    """
    Local context for testing a processing pipeline without executing a real job on Picsellia.
    """

    def __init__(
        self,
        processing_parameters_cls: type[TParameters],
        processing_parameters: dict[str, Any] | None = None,
        api_token: str | None = None,
        host: str | None = None,
        organization_id: str | None = None,
        organization_name: str | None = None,
        job_id: str | None = None,
        job_type: ProcessingType | None = None,
        input_dataset_version_id: str | None = None,
        output_dataset_version_id: str | None = None,
        output_dataset_version_name: str | None = None,
        use_id: bool | None = True,
        download_annotations: bool | None = True,
        model_version_id: str | None = None,
        working_dir: str | None = None,
    ):
        """
        Initialize the local processing context.

        Can create or retrieve dataset versions and model versions as needed.

        Raises:
            ValueError: If required data is missing (e.g., input dataset version).
        """
        super().__init__(
            api_token=api_token,
            host=host,
            organization_id=organization_id,
            organization_name=organization_name,
            working_dir=working_dir,
        )

        self.job_id = job_id
        self.job_type = job_type
        self.input_dataset_version_id = input_dataset_version_id
        self.output_dataset_version_id = output_dataset_version_id
        self.model_version_id = model_version_id

        if self.input_dataset_version_id:
            self.input_dataset_version = self.get_dataset_version(
                self.input_dataset_version_id
            )

        if self.output_dataset_version_id:
            self.output_dataset_version = self.get_dataset_version(
                self.output_dataset_version_id
            )
        elif output_dataset_version_name:
            self.output_dataset_version = self.client.get_dataset_by_id(
                self.input_dataset_version.origin_id
            ).create_version(version=output_dataset_version_name)
            self.output_dataset_version_id = self.output_dataset_version.id

        if self.model_version_id:
            self.model_version = self.get_model_version()

        self.processing_parameters = processing_parameters_cls(
            log_data=processing_parameters or {}
        )
        self.use_id = use_id
        self.download_annotations = download_annotations

    @property
    def working_dir(self) -> str:
        """Return the working directory for this job."""
        if self._working_dir_override:
            return self._working_dir_override
        return os.path.join(os.getcwd(), f"job_{self.job_id}")

    def get_dataset_version(self, dataset_version_id) -> DatasetVersion:
        """Fetch a dataset version by its ID."""
        return self.client.get_dataset_version_by_id(dataset_version_id)

    def get_model_version(self) -> ModelVersion:
        """Fetch a model version by its ID."""
        return self.client.get_model_version_by_id(self.model_version_id)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to a dictionary for logging or serialization."""
        return {
            "context_parameters": {
                "host": self.host,
                "organization_id": self.organization_id,
                "job_type": self.job_type,
                "input_dataset_version_id": self.input_dataset_version_id,
                "output_dataset_version_id": self.output_dataset_version_id,
                "model_version_id": self.model_version_id,
                "use_id": self.use_id,
            },
            "processing_parameters": self._process_parameters(
                parameters_dict=self.processing_parameters.to_dict(),
                defaulted_keys=self.processing_parameters.defaulted_keys,
            ),
        }
