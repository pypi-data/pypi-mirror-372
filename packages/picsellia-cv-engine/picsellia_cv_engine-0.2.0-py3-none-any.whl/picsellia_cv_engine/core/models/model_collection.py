import os
from typing import Any, Generic, TypeVar

from .model import Model

TModel = TypeVar("TModel", bound=Model)


class ModelCollection(Generic[TModel]):
    """
    A collection for managing multiple models, with one active loaded model at a time.

    Provides access to individual models by name, and supports downloading weights
    for all models in the collection.
    """

    def __init__(self, models: list[TModel]):
        """
        Initialize the collection from a list of models.

        Args:
            models (list[TModel]): List of model instances.
        """
        self.models = {model.name: model for model in models}
        self._loaded_model: Any | None = None

    @property
    def loaded_model(self) -> Any:
        """
        Return the currently loaded model.

        Raises:
            ValueError: If no model is currently loaded.
        """
        if self._loaded_model is None:
            raise ValueError("No model is currently loaded in this collection.")
        return self._loaded_model

    def set_loaded_model(self, model: Any) -> None:
        """Set the loaded model for this collection."""
        self._loaded_model = model

    def __getitem__(self, key: str) -> TModel:
        """
        Access a model by name.

        Args:
            key (str): The model name.

        Returns:
            TModel: The corresponding model.
        """
        return self.models[key]

    def __setitem__(self, key: str, value: TModel):
        """
        Add or update a model in the collection.

        Args:
            key (str): The model name.
            value (TModel): The model instance.
        """
        self.models[key] = value

    def __iter__(self):
        """Iterate over models in the collection."""
        return iter(self.models.values())

    def download_weights(self, destination_dir: str) -> None:
        """
        Download weights for all models to subdirectories by model name.

        Args:
            destination_dir (str): Base directory where weights will be saved.
        """
        for model in self:
            model.download_weights(
                destination_dir=os.path.join(destination_dir, model.name)
            )


TModelCollection = TypeVar("TModelCollection", bound=ModelCollection)
