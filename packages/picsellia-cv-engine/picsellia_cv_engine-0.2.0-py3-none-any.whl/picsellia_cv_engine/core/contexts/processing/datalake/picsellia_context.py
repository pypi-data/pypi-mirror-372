import os
from typing import Any, Generic, TypeVar
from uuid import UUID

import picsellia  # type: ignore
import requests
from picsellia import Datalake, ModelVersion
from picsellia.types.enums import ProcessingType

from picsellia_cv_engine.core.contexts import PicselliaContext
from picsellia_cv_engine.core.parameters import Parameters

TParameters = TypeVar("TParameters", bound=Parameters)


class PicselliaDatalakeProcessingContext(PicselliaContext, Generic[TParameters]):
    """
    Context for running Picsellia datalake processing jobs.

    Manages job initialization, model version, input/output datalakes, and job parameters.
    """

    def __init__(
        self,
        processing_parameters_cls: type[TParameters],
        api_token: str | None = None,
        host: str | None = None,
        organization_id: str | None = None,
        organization_name: str | None = None,
        job_id: str | None = None,
        use_id: bool | None = True,
        working_dir: str | None = None,
    ):
        """
        Initialize the datalake processing context.

        Raises:
            ValueError: If required information is missing (e.g., job ID or input datalake).
        """
        super().__init__(
            api_token=api_token,
            host=host,
            organization_id=organization_id,
            organization_name=organization_name,
            working_dir=working_dir,
        )

        self.job_id = job_id or os.environ.get("job_id")
        if not self.job_id:
            raise ValueError(
                "Job ID not provided. Please provide it as an argument or set the 'job_id' environment variable."
            )

        self.job = self._initialize_job()
        self.job_type = self.job.sync()["type"]
        self.job_context = self._initialize_job_context()

        self._model_version_id = self.job_context.get("model_version_id")
        self._input_datalake_id = self.job_context.get("input_datalake_id")
        self._output_datalake_id = self.job_context.get("output_datalake_id")
        self._payload_presigned_url = self.job_context.get("payload_presigned_url")

        if self._input_datalake_id:
            self.input_datalake = self.get_datalake(self._input_datalake_id)
        else:
            raise ValueError("Input datalake ID not found.")

        self.output_datalake = (
            self.get_datalake(self._output_datalake_id)
            if self._output_datalake_id
            else None
        )
        self.model_version = (
            self.get_model_version() if self._model_version_id else None
        )
        self.data_ids = self.get_data_ids()

        self.use_id = use_id

        self.processing_parameters = processing_parameters_cls(
            log_data=self.job_context["parameters"]
        )

    @property
    def working_dir(self) -> str:
        """Return the working directory path for the job."""
        if self._working_dir_override:
            return self._working_dir_override
        return os.path.join(os.getcwd(), f"job_{self.job_id}")

    @property
    def model_version_id(self) -> str | None:
        """
        Get the model version ID, validating presence if required.

        Raises:
            ValueError: If required for pre-annotation but missing.
        """
        if (
            not self._model_version_id
            and self.job_type == ProcessingType.PRE_ANNOTATION
        ):
            raise ValueError("Model version ID is required for pre-annotation jobs.")
        return self._model_version_id

    def to_dict(self) -> dict[str, Any]:
        """Convert the context to a dictionary representation."""
        return {
            "context_parameters": {
                "host": self.host,
                "organization_id": self.organization_id,
                "job_id": self.job_id,
            },
            "model_version_id": self.model_version_id,
            "input_datalake_id": self._input_datalake_id,
            "output_datalake_id": self._output_datalake_id,
            "processing_parameters": self._process_parameters(
                parameters_dict=self.processing_parameters.to_dict(),
                defaulted_keys=self.processing_parameters.defaulted_keys,
            ),
        }

    def _initialize_job_context(self) -> dict[str, Any]:
        """Fetch and return the job's context data."""
        return self.job.sync()["datalake_processing_job"]

    def _initialize_job(self) -> picsellia.Job:
        """Fetch the Picsellia Job from its ID."""
        return self.client.get_job_by_id(self.job_id)

    def get_datalake(self, datalake_id: str) -> Datalake:
        """Fetch a datalake by ID."""
        return self.client.get_datalake(id=datalake_id)

    def get_model_version(self) -> ModelVersion:
        """Fetch the model version by ID."""
        return self.client.get_model_version_by_id(self.model_version_id)

    def get_data_ids(self) -> list[UUID]:
        """
        Retrieve data IDs from the job payload.

        Raises:
            ValueError: If the payload URL is missing or invalid.
        """
        if self._payload_presigned_url:
            payload = requests.get(self._payload_presigned_url).json()
            return [UUID(data_id) for data_id in payload["data_ids"]]
        else:
            raise ValueError("Payload presigned URL not found.")
