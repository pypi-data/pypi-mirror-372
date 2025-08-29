import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any

from picsellia.types.enums import LogType
from PIL import Image, ImageDraw

from picsellia_cv_engine.core import CocoDataset, DatasetCollection
from picsellia_cv_engine.core.contexts import (
    LocalTrainingContext,
    PicselliaTrainingContext,
)
from picsellia_cv_engine.frameworks.sam2.model.model import SAM2Model


class Sam2Trainer:
    """
    Trainer class for managing the full fine-tuning process of a SAM2 model using a COCO dataset.
    This class handles data preparation, training launch, and checkpoint saving.
    """

    def __init__(
        self,
        model: SAM2Model,
        dataset_collection: DatasetCollection[CocoDataset],
        context: PicselliaTrainingContext | LocalTrainingContext,
        sam2_repo_path: str,
    ):
        """
        Initializes the trainer with the model, dataset, context, and SAM2 repository path.

        Args:
            model (Model): Picsellia model instance containing paths and metadata.
            dataset_collection (DatasetCollection[CocoDataset]): Dataset collection containing the training data.
            context: Training context containing hyperparameters and working directory.
            sam2_repo_path (str): Path to the local SAM2 repository.
        """
        self.model = model
        self.dataset_collection = dataset_collection
        self.context = context
        self.sam2_repo_path = sam2_repo_path

        self.img_root = os.path.join(sam2_repo_path, "data", "JPEGImages")
        self.ann_root = os.path.join(sam2_repo_path, "data", "Annotations")
        prepare_directories(self.img_root, self.ann_root)

    def prepare_data(self) -> str:
        """
        Prepares the training data by converting COCO annotations to PNG masks.

        Returns:
            str: The filename of the pretrained weights.
        """
        source_images = self.dataset_collection["train"].images_dir
        source_annotations = self.dataset_collection["train"].annotations_dir
        coco_file = next(
            f for f in os.listdir(source_annotations) if f.endswith(".json")
        )
        coco_path = os.path.join(source_annotations, coco_file)

        shutil.copy(
            coco_path, os.path.join(self.context.working_dir, "coco_annotations.json")
        )
        shutil.copy(
            self.model.pretrained_weights_path,
            os.path.join(self.sam2_repo_path, "checkpoints"),
        )

        pretrained_weights_name = os.path.basename(self.model.pretrained_weights_path)
        self.model.pretrained_weights_path = os.path.join(
            self.sam2_repo_path, "checkpoints", pretrained_weights_name
        )

        coco = load_coco_annotations(
            os.path.join(self.context.working_dir, "coco_annotations.json")
        )
        convert_coco_to_png_masks(coco, source_images, self.img_root, self.ann_root)
        normalize_filenames([self.img_root, self.ann_root])

        return pretrained_weights_name

    def launch_training(self, pretrained_weights_name: str) -> str:
        """
        Launches the SAM2 training process.

        Args:
            pretrained_weights_name (str): Filename of the checkpoint to use as pretrained weights.

        Returns:
            str: Path to the trained checkpoint file.

        Raises:
            subprocess.CalledProcessError: If the training process fails.
        """
        experiment_log_dir = os.path.join(self.model.results_dir, "sam2_logs")
        os.makedirs(experiment_log_dir, exist_ok=True)

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [
                self.sam2_repo_path,
                os.path.join(self.sam2_repo_path, "training"),
            ]
        )

        log_file = os.path.join(experiment_log_dir, "train_stdout.log")

        overrides = [
            f"scratch.train_batch_size={self.context.hyperparameters.batch_size}",
            f"scratch.resolution={self.context.hyperparameters.image_size}",
            f"scratch.base_lr={self.context.hyperparameters.learning_rate}",
            f"scratch.num_epochs={self.context.hyperparameters.epochs}",
            f"trainer.checkpoint.model_weight_initializer.state_dict.checkpoint_path=checkpoints/{pretrained_weights_name}",
        ]

        self.model.results_dir = os.path.join(
            self.sam2_repo_path, "sam2_logs", "configs", "train.yaml"
        )

        command = [
            sys.executable,
            "-m",
            "training.train",
            "-c",
            "configs/train.yaml",
            "--use-cluster",
            "0",
            "--num-gpus",
            "1",
            *overrides,
        ]

        process = subprocess.Popen(
            command,
            cwd=self.sam2_repo_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        parse_and_log_sam2_output(
            process=process, context=self.context, log_file_path=log_file
        )

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        return os.path.join(self.model.results_dir, "checkpoints", "checkpoint.pt")

    def save_checkpoint(self, checkpoint_path: str):
        """
        Saves the final model checkpoint as an artifact in the Picsellia experiment.

        Args:
            checkpoint_path (str): Path to the trained model checkpoint.

        Raises:
            FileNotFoundError: If the checkpoint file is not found.
        """
        if os.path.exists(checkpoint_path):
            self.model.save_artifact_to_experiment(
                experiment=self.context.experiment,
                artifact_name="model-latest",
                artifact_path=checkpoint_path,
            )
            self.model.trained_weights_path = checkpoint_path
        else:
            raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")


def prepare_directories(img_root: str, ann_root: str):
    """
    Creates required directories for image and annotation data.

    Args:
        img_root (str): Path to the image directory.
        ann_root (str): Path to the annotation directory.
    """
    os.makedirs(img_root, exist_ok=True)
    os.makedirs(ann_root, exist_ok=True)


def load_coco_annotations(coco_path: str) -> dict[str, Any]:
    """
    Loads COCO-format annotations from a JSON file.

    Args:
        coco_path (str): Path to the COCO annotations file.

    Returns:
        dict[str, Any]: Parsed JSON dictionary.
    """
    with open(coco_path) as f:
        return json.load(f)


def generate_mask(width: int, height: int, annotations: list[dict]) -> Image.Image:
    """
    Generates a PNG mask from COCO-style polygon annotations.

    Args:
        width (int): Width of the mask.
        height (int): Height of the mask.
        annotations (list): List of annotation objects.

    Returns:
        Image.Image: The generated mask image.
    """
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    object_idx = 1
    for ann in annotations:
        if ann.get("iscrowd", 0) == 1 or "segmentation" not in ann:
            continue
        for seg in ann["segmentation"]:
            if isinstance(seg, list) and len(seg) >= 6:
                poly = [(seg[i], seg[i + 1]) for i in range(0, len(seg), 2)]
                draw.polygon(poly, fill=object_idx)
                object_idx += 1
    return mask


def convert_coco_to_png_masks(
    coco: dict, source_images: str, img_root: str, ann_root: str
):
    """
    Converts COCO annotations to PNG masks and organizes them in folders.

    Args:
        coco (dict): Loaded COCO annotations.
        source_images (str): Directory containing original image files.
        img_root (str): Destination directory for images.
        ann_root (str): Destination directory for annotations.
    """
    images_by_id = {img["id"]: img for img in coco["images"]}
    annotations_by_image: dict[str, Any] = {}
    for ann in coco["annotations"]:
        annotations_by_image.setdefault(ann["image_id"], []).append(ann)

    for img_id, annotations in annotations_by_image.items():
        img_info = images_by_id[img_id]
        width, height = img_info["width"], img_info["height"]
        original_file = img_info["file_name"]
        base_name = os.path.splitext(original_file)[0]

        video_img_dir = os.path.join(img_root, base_name)
        video_ann_dir = os.path.join(ann_root, base_name)
        os.makedirs(video_img_dir, exist_ok=True)
        os.makedirs(video_ann_dir, exist_ok=True)

        shutil.copy(
            os.path.join(source_images, original_file),
            os.path.join(video_img_dir, "00000.jpg"),
        )

        mask = generate_mask(width, height, annotations)
        mask.save(os.path.join(video_ann_dir, "00000.png"))


def normalize_filenames(root_dirs: list[str]):
    """
    Normalizes filenames in a list of directories to avoid naming conflicts.

    Args:
        root_dirs (list[str]): List of directory paths.
    """
    for root in root_dirs:
        for subdir, _, files in os.walk(root):
            for name in files:
                new_name = name.replace(".", "_", name.count(".") - 1)
                if not re.search(r"_\d+\.\w+$", new_name):
                    new_name = new_name.replace(".", "_1.")
                os.rename(os.path.join(subdir, name), os.path.join(subdir, new_name))


def parse_and_log_sam2_output(
    process: subprocess.Popen[str],
    context: PicselliaTrainingContext | LocalTrainingContext,
    log_file_path: str,
) -> None:
    """
    Parses SAM2 training output and logs metrics into the Picsellia experiment.

    Args:
        process: Subprocess running the training script.
        context: Picsellia pipeline context used for logging.
        log_file_path (str): File to store raw stdout logs from the training process.
    """
    meter_pattern = re.compile(r"Losses and meters:\s+({.*})")

    METRIC_NAME_MAPPING = {
        "Losses/train_all_loss": "train/total_loss",
        "Losses/train_all_loss_mask": "train/loss_mask",
        "Losses/train_all_loss_dice": "train/loss_dice",
        "Losses/train_all_loss_iou": "train/loss_iou",
        "Losses/train_all_loss_class": "train/loss_class",
        "Losses/train_all_core_loss": "train/loss_core",
        "Trainer/epoch": "train/epoch",
        "Trainer/steps_train": "train/step",
    }

    SKIPPED_METRICS = {"Trainer/where"}

    with open(log_file_path, "w") as log_file:
        if process.stdout is None:
            raise RuntimeError("process.stdout is None. Cannot read training output.")

        for line in process.stdout:
            print(line, end="")
            log_file.write(line)

            match = meter_pattern.search(line)
            if match:
                try:
                    metrics_str = match.group(1)
                    metrics = json.loads(metrics_str.replace("'", '"'))
                    for name, value in metrics.items():
                        if name in SKIPPED_METRICS or not isinstance(
                            value, float | int
                        ):
                            continue

                        log_name = METRIC_NAME_MAPPING.get(
                            name, f"train/{name.replace('/', '_')}"
                        )
                        context.experiment.log(
                            name=log_name,
                            data=value,
                            type=LogType.LINE,
                        )
                except Exception as e:
                    print(f"⚠️ Failed to parse SAM2 metrics: {e}")
