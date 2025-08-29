from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.contexts import PicselliaDatasetProcessingContext
from picsellia_cv_engine.core.models import PicselliaRectanglePrediction
from picsellia_cv_engine.frameworks.grounding_dino.model.model import GroundingDinoModel
from picsellia_cv_engine.frameworks.grounding_dino.services.predictor import (
    GroundingDinoDetectionModelPredictor,
)


@step
def run_grounding_dino_inference(
    model: GroundingDinoModel, dataset: CocoDataset
) -> list[PicselliaRectanglePrediction]:
    context: PicselliaDatasetProcessingContext = Pipeline.get_active_context()
    parameters = context.processing_parameters.to_dict()

    label_names = [cat["name"] for cat in dataset.coco_data.get("categories", [])]

    predictor = GroundingDinoDetectionModelPredictor(
        model=model,
        label_names=label_names,
        box_threshold=parameters.get("box_threshold"),
        text_threshold=parameters.get("text_threshold"),
    )

    image_paths = predictor.pre_process_dataset(dataset=dataset)
    batches = predictor.prepare_batches(image_paths, batch_size=4)
    results = predictor.run_inference_on_batches(batches)
    predictions = predictor.post_process_batches(
        image_batches=batches,
        batch_results=results,
        dataset=dataset,
    )

    return predictions
