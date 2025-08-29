from groundingdino.util.inference import Model as grounding_dino_model

from picsellia_cv_engine.core.models import Model


class GroundingDinoModel(Model):
    def load_weights(self, weights_path: str, config_path: str) -> grounding_dino_model:
        return grounding_dino_model(
            model_config_path=config_path,
            model_checkpoint_path=weights_path,
        )
