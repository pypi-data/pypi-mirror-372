import torch

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.contexts import PicselliaDatasetProcessingContext
from picsellia_cv_engine.frameworks.clip.model.model import CLIPModel
from picsellia_cv_engine.frameworks.clip.services.predictor import (
    CLIPModelPredictor,
    PicselliaCLIPEmbeddingPrediction,
)


@step
def predict(
    model: CLIPModel, dataset: CocoDataset
) -> list[PicselliaCLIPEmbeddingPrediction]:
    """
    Inference step for CLIP on an image-only dataset.

    This step extracts image embeddings using the provided CLIP model and dataset.

    Args:
        model: The CLIP model instance with loaded weights and processor.
        dataset: A COCO-style dataset containing image assets.

    Returns:
        A list of predictions with image embeddings for each asset in the dataset.
    """
    context: PicselliaDatasetProcessingContext = Pipeline.get_active_context()
    parameters = context.processing_parameters.to_dict()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    predictor = CLIPModelPredictor(model=model, device=device)
    image_paths = predictor.pre_process_dataset(dataset)
    image_batches = predictor.prepare_batches(
        image_paths, batch_size=parameters.get("batch_size", 4)
    )
    results = predictor.run_image_inference_on_batches(image_batches)
    predictions = predictor.post_process_image_batches(
        image_batches=image_batches,
        batch_results=results,
        dataset=dataset,
    )

    return predictions
