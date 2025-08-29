import os

import torch

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.contexts import PicselliaTrainingContext
from picsellia_cv_engine.frameworks.clip.model.model import CLIPModel
from picsellia_cv_engine.frameworks.clip.services.evaluator import (
    generate_embeddings_from_results,
    run_umap_dbscan_clustering,
    save_clustering_visualizations,
)
from picsellia_cv_engine.frameworks.clip.services.predictor import CLIPModelPredictor


@step()
def evaluate(model: CLIPModel, dataset: CocoDataset):
    """
    Evaluate a CLIP model on an image-only dataset using clustering.

    This step:
    - Loads the trained CLIP model and processor.
    - Runs inference on the dataset to extract image embeddings.
    - Applies UMAP to reduce dimensionality.
    - Uses DBSCAN to identify clusters in the embedding space.
    - Saves and logs clustering visualizations (UMAP plot, cluster image grids, outliers).

    Args:
        model (CLIPModel): The trained CLIP model to evaluate.
        dataset (CocoDataset): The image dataset to evaluate the model on.

    Raises:
        FileNotFoundError: If no trained weights are found in the model.
    """
    context: PicselliaTrainingContext = Pipeline.get_active_context()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if not model.trained_weights_path:
        raise FileNotFoundError("No trained weights path found in model.")

    loaded_model, loaded_processor = model.load_weights(
        weights_path=model.trained_weights_path,
        repo_id=context.hyperparameters.model_name,
    )
    model.set_loaded_model(loaded_model)
    model.set_loaded_processor(loaded_processor)

    predictor = CLIPModelPredictor(model=model, device=device)
    image_paths = predictor.pre_process_dataset(dataset)
    image_batches = predictor.prepare_batches(
        image_paths, batch_size=context.hyperparameters.batch_size
    )
    results = predictor.run_image_inference_on_batches(image_batches)
    embeddings, paths = generate_embeddings_from_results(image_batches, results)

    reduced, labels, best_eps = run_umap_dbscan_clustering(embeddings)

    evaluation_dir = os.path.join(model.results_dir, "clip_evaluation")
    save_clustering_visualizations(
        reduced_embeddings=reduced,
        cluster_labels=labels,
        image_paths=paths,
        results_dir=evaluation_dir,
        log_images=True,
        experiment=context.experiment,
    )
