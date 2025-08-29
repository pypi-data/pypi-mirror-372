from typing import Any

import torch
from picsellia import Label, ModelVersion
from transformers import CLIPModel as TransformerCLIPModel
from transformers import CLIPProcessor as TransformerCLIPProcessor

from picsellia_cv_engine.core.models import Model


class CLIPModel(Model):
    """
    CLIP model wrapper for managing weights, processor, and runtime configurations.
    """

    def __init__(
        self,
        name: str,
        model_version: ModelVersion,
        pretrained_weights_name: str | None = None,
        trained_weights_name: str | None = None,
        config_name: str | None = None,
        exported_weights_name: str | None = None,
        labelmap: dict[str, Label] | None = None,
    ):
        """
        Initialize the CLIP model.

        Args:
            name: Name of the model.
            model_version: Associated Picsellia ModelVersion.
            pretrained_weights_name: Optional name of the pretrained weights file.
            trained_weights_name: Optional name of the trained weights file.
            config_name: Optional name of the config file.
            exported_weights_name: Optional name of the exported weights file.
            labelmap: Optional dictionary mapping label names to Picsellia Label objects.
        """
        super().__init__(
            name=name,
            model_version=model_version,
            pretrained_weights_name=pretrained_weights_name,
            trained_weights_name=trained_weights_name,
            config_name=config_name,
            exported_weights_name=exported_weights_name,
            labelmap=labelmap,
        )
        self._loaded_processor: Any | None = None

    @property
    def loaded_processor(self) -> Any:
        """
        Return the loaded processor instance.

        Returns:
            The loaded processor.

        Raises:
            ValueError: If the processor has not been loaded yet.
        """
        if self._loaded_processor is None:
            raise ValueError(
                "Processor is not loaded. Please load the processor before accessing it."
            )
        return self._loaded_processor

    def set_loaded_processor(self, processor: Any) -> None:
        """
        Set the processor instance after loading it at runtime.

        Args:
            processor: The processor instance to attach to the model.
        """
        self._loaded_processor = processor

    def load_weights(
        self, weights_path: str, repo_id: str = "openai/clip-vit-large-patch14-336"
    ) -> tuple[TransformerCLIPModel, TransformerCLIPProcessor]:
        """
        Load model weights and processor from the specified path and Hugging Face repository.

        Args:
            weights_path: Local path to the model weights.
            repo_id: Identifier of the Hugging Face model to load the processor from.

        Returns:
            A tuple containing the CLIP model and its processor, both loaded and ready for inference.
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = TransformerCLIPModel.from_pretrained(weights_path).to(device).eval()
        processor = TransformerCLIPProcessor.from_pretrained(repo_id)
        return model, processor
