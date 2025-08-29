import os

import numpy as np
from PIL import Image
from sam2.sam2_image_predictor import SAM2ImagePredictor

from picsellia_cv_engine.core import CocoDataset
from picsellia_cv_engine.core.services.utils.annotations import mask_to_polygons


class SAM2ModelPredictor:
    def __init__(self, predictor: SAM2ImagePredictor):
        self.predictor = predictor

    def pre_process_dataset(self, dataset: CocoDataset) -> list[np.ndarray]:
        """
        Collects image file paths from the dataset.

        Args:
            dataset (CocoDataset): Dataset object containing image directory.

        Returns:
            list[str]: List of full paths to image files.
        """
        images = []
        for f in os.listdir(dataset.images_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(dataset.images_dir, f)
                img = Image.open(image_path).convert("RGB")
                img_np = np.array(img)
                images.append(img_np)
        return images

    def preprocess_images(self, image_list: list[np.ndarray]):
        self.predictor.set_image_batch(image_list=image_list)

    def preprocess(self, image: np.ndarray):
        self.predictor.set_image(image=image)

    def run_inference(
        self,
        point_coords: np.ndarray | None = None,
        point_labels: np.ndarray | None = None,
        box: np.ndarray | None = None,
        mask_input: np.ndarray | None = None,
        multimask_output: bool = True,
    ):
        masks, ious, _ = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            box=box,
            mask_input=mask_input,
            multimask_output=multimask_output,
        )

        mask_dicts = [
            {"segmentation": masks[i], "score": float(ious[i])}
            for i in range(len(masks))
        ]
        return mask_dicts

    def post_process(self, results: list[dict]) -> list[dict]:
        """
        Converts mask predictions to polygons and associates them with their scores.

        Args:
            results (list[dict]): List of dictionaries with keys "segmentation" and "score".

        Returns:
            list[dict]: List of {"polygon": [...], "score": float} dictionaries.
        """
        polygons_with_scores = []

        for mask_dict in results:
            mask = mask_dict.get("segmentation")
            score = mask_dict.get("score")

            if mask is None:
                continue

            poly_list = mask_to_polygons(mask.astype(np.uint8))

            for poly in poly_list:
                if len(poly) == 0:
                    continue
                polygons_with_scores.append(
                    {"polygon": [[int(x), int(y)] for x, y in poly], "score": score}
                )

        return polygons_with_scores
