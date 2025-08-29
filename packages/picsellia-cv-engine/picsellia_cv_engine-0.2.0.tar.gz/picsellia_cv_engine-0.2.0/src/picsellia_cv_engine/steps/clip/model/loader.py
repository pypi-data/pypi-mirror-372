import logging

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.contexts import (
    PicselliaDatalakeProcessingContext,
    PicselliaDatasetProcessingContext,
)
from picsellia_cv_engine.core.services.model.utils import build_model_impl
from picsellia_cv_engine.frameworks.clip.model.model import CLIPModel

logger = logging.getLogger(__name__)


@step
def load_model(
    pretrained_weights_name: str,
    trained_weights_name: str | None = None,
    config_name: str | None = None,
    exported_weights_name: str | None = None,
    repo_id: str = "openai/clip-vit-large-patch14-336",
) -> CLIPModel:
    """
    Load a CLIP model using the Picsellia model interface.

    Args:
        pretrained_weights_name: Name of the pretrained weights artifact.
        trained_weights_name: Optional name of the trained weights.
        config_name: Optional name of the model config file.
        exported_weights_name: Optional name of exported weights for evaluation or inference.
        repo_id: HuggingFace repo ID used for loading the processor (default is OpenAI's ViT-L/14-336).

    Returns:
        A loaded instance of CLIPModel, ready for inference.

    Raises:
        FileNotFoundError: If no pretrained weights path is found on the model.
    """
    context: PicselliaDatasetProcessingContext | PicselliaDatalakeProcessingContext = (
        Pipeline.get_active_context()
    )

    model = build_model_impl(
        context=context,
        model_cls=CLIPModel,
        pretrained_weights_name=pretrained_weights_name,
        trained_weights_name=trained_weights_name,
        config_name=config_name,
        exported_weights_name=exported_weights_name,
    )

    if not model.pretrained_weights_path:
        raise FileNotFoundError("No pretrained weights path found in model.")

    loaded_model, loaded_processor = model.load_weights(
        weights_path=model.pretrained_weights_path, repo_id=repo_id
    )
    model.set_loaded_model(loaded_model)
    model.set_loaded_processor(loaded_processor)

    return model
