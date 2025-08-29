import os
from abc import ABC, abstractmethod
from typing import Any

import picsellia

from picsellia_cv_engine.core.logging.colors import Colors


class PicselliaContext(ABC):
    def __init__(
        self,
        api_token: str | None = None,
        host: str | None = None,
        organization_id: str | None = None,
        organization_name: str | None = None,
        working_dir: str | None = None,
    ):
        """
        Base class for defining a context within the Picsellia platform.

        This context manages authentication and client setup for interacting with Picsellia.
        It must be subclassed to define a specific working directory once an identifier
        (e.g., experiment ID or job ID) becomes available.

        Args:
            api_token (Optional[str]): API token used to authenticate with the Picsellia API.
                If not provided, the value is read from the 'api_token' environment variable.
            host (Optional[str]): Host URL of the Picsellia server. Defaults to 'https://app.picsellia.com'.
            organization_id (Optional[str]): ID of the Picsellia organization. Can also be set via the 'organization_id' env variable.
            organization_name (Optional[str]): Name of the Picsellia organization. Can also be set via the 'organization_name' env variable.
            working_dir (Optional[str]): Optional override for the working directory.
        """
        self.api_token = api_token or os.getenv("api_token")

        if not self.api_token:
            raise ValueError(
                "API token not provided. Please provide it as an argument or set the 'api_token' environment variable."
            )

        self.host = host or os.getenv("host", "https://app.picsellia.com")
        self.organization_id = organization_id or os.getenv("organization_id")
        self.organization_name = organization_name or os.getenv("organization_name")

        self.client = self._initialize_client()

        self._working_dir_override = working_dir

    @property
    @abstractmethod
    def working_dir(self) -> str:
        """
        Abstract property to define the working directory path.

        This should be implemented by subclasses to specify where files such as
        datasets, weights, and logs are stored locally.

        Returns:
            str: Path to the working directory.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must define a working_dir.")

    def _initialize_client(self) -> picsellia.Client:
        """
        Initializes the Picsellia client for API interaction.

        Returns:
            picsellia.Client: An authenticated client object.
        """
        return picsellia.Client(
            api_token=self.api_token,
            host=self.host,
            organization_id=self.organization_id,
            organization_name=self.organization_name,
        )

    def _format_parameter_with_color_and_suffix(
        self, value: Any, key: str, defaulted_keys: set
    ) -> str:
        """
        Formats a parameter value with color and an optional default suffix.

        Adds color formatting (using ANSI codes) and a "(default)" label if the key
        belongs to the set of defaulted keys.

        Args:
            value (Any): The value to format.
            key (str): The parameter key.
            defaulted_keys (set): Set of keys that were set to default values.

        Returns:
            str: The formatted string with color and suffix.
        """
        suffix = " (default)" if key in defaulted_keys else ""
        color_code = Colors.YELLOW if suffix else Colors.CYAN
        return f"{color_code}{value}{Colors.ENDC}{suffix}"

    def _process_parameters(self, parameters_dict: dict, defaulted_keys: set) -> dict:
        """
        Applies formatting to a dictionary of parameters based on whether they were defaulted.

        Args:
            parameters_dict (dict): The dictionary of parameters to format.
            defaulted_keys (set): Keys that indicate which parameters were set to default values.

        Returns:
            dict: A new dictionary with formatted string values.
        """
        processed_params = {}
        for key, value in parameters_dict.items():
            processed_params[key] = self._format_parameter_with_color_and_suffix(
                value, key, defaulted_keys
            )
        return processed_params

    @abstractmethod
    def to_dict(self):
        """
        Converts the context to a dictionary representation.

        This method should be implemented by subclasses to expose their internal
        parameters and configuration for logging or serialization purposes.
        """
        pass
