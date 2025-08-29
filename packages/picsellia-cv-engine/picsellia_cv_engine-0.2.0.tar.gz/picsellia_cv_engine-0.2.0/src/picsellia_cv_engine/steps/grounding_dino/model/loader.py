import logging

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.contexts import PicselliaDatasetProcessingContext
from picsellia_cv_engine.core.services.model.utils import build_model_impl
from picsellia_cv_engine.frameworks.grounding_dino.model.model import GroundingDinoModel

logger = logging.getLogger(__name__)


@step
def load_grounding_dino_model(
    pretrained_weights_name: str,
    trained_weights_name: str | None = None,
    config_name: str | None = None,
    exported_weights_name: str | None = None,
) -> GroundingDinoModel:
    context: PicselliaDatasetProcessingContext = Pipeline.get_active_context()

    model = build_model_impl(
        context=context,
        model_cls=GroundingDinoModel,
        pretrained_weights_name=pretrained_weights_name,
        trained_weights_name=trained_weights_name,
        config_name=config_name,
        exported_weights_name=exported_weights_name,
    )

    if not model.pretrained_weights_path:
        raise FileNotFoundError("No pretrained weights path found in model.")

    loaded_model = model.load_weights(
        weights_path=model.pretrained_weights_path, config_path=model.config_path
    )
    model.set_loaded_model(loaded_model)
    return model
