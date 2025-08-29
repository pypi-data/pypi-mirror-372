import sys

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import CocoDataset, DatasetCollection
from picsellia_cv_engine.core.contexts import (
    LocalTrainingContext,
    PicselliaTrainingContext,
)
from picsellia_cv_engine.frameworks.sam2.model.model import SAM2Model
from picsellia_cv_engine.frameworks.sam2.services.trainer import Sam2Trainer


@step()
def train(
    model: SAM2Model,
    dataset_collection: DatasetCollection[CocoDataset],
    sam2_repo_path: str,
):
    """
    Training step for fine-tuning a SAM2 model on a custom dataset.

    This step prepares the dataset and masks, configures the environment, and launches the SAM2 training loop.

    Args:
        model (Model): The Picsellia model instance containing pretrained weights and logging context.
        dataset_collection (DatasetCollection[CocoDataset]): The dataset collection for training, expected to include a 'train' split.
        sam2_repo_path (str): Path to the local SAM2 repository used for training.
    """
    context: PicselliaTrainingContext | LocalTrainingContext = (
        Pipeline.get_active_context()
    )
    sys.path.insert(0, sam2_repo_path)

    trainer = Sam2Trainer(
        model=model,
        dataset_collection=dataset_collection,
        context=context,
        sam2_repo_path=sam2_repo_path,
    )

    pretrained_weights_name = trainer.prepare_data()
    checkpoint_path = trainer.launch_training(pretrained_weights_name)
    trainer.save_checkpoint(checkpoint_path)
