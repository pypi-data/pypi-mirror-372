from picsellia import Asset
from picsellia.sdk.asset import MultiAsset
from picsellia.types.enums import InferenceType

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core.models.picsellia_prediction import (
    PicselliaClassificationPrediction,
    PicselliaOCRPrediction,
    PicselliaPolygonPrediction,
    PicselliaRectanglePrediction,
)
from picsellia_cv_engine.core.services.model.utils import evaluate_model_impl


@step
def evaluate_model(
    picsellia_predictions: (
        list[PicselliaClassificationPrediction]
        | list[PicselliaRectanglePrediction]
        | list[PicselliaPolygonPrediction]
        | list[PicselliaOCRPrediction]
    ),
    inference_type: InferenceType,
    assets: list[Asset] | MultiAsset,
    output_dir: str,
) -> None:
    """
    Perform evaluation of model predictions against ground truth annotations using Picsellia's ModelEvaluator.

    This step supports multiple inference types including classification, object detection, segmentation, and OCR.
    It compares the provided model predictions to the actual asset annotations, computes evaluation metrics,
    and stores the results in the specified output directory.

    Args:
        picsellia_predictions (List[Union[PicselliaClassificationPrediction, PicselliaRectanglePrediction, PicselliaPolygonPrediction, PicselliaOCRPrediction]]):
            List of model predictions corresponding to a supported inference type.

        inference_type (InferenceType):
            The type of inference performed (e.g., CLASSIFICATION, DETECTION, SEGMENTATION, OCR).

        assets (Union[List[Asset], MultiAsset]):
            The ground truth dataset assets to evaluate against.

        output_dir (str):
            The path to the directory where evaluation results will be saved (e.g., confusion matrix, metrics report).
    """
    context = Pipeline.get_active_context()
    return evaluate_model_impl(
        context=context,
        picsellia_predictions=picsellia_predictions,
        inference_type=inference_type,
        assets=assets,
        output_dir=output_dir,
    )
