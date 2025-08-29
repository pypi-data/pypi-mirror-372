import cv2
import numpy as np


def mask_to_polygons(mask: np.ndarray) -> list[np.ndarray]:
    """
    Convert a binary segmentation mask into a list of polygons.

    This function extracts the external contours from a 2D binary mask
    and converts them into polygon representations. Each polygon is a
    NumPy array of (x, y) coordinates. Contours with fewer than 3 points
    are discarded to ensure valid polygon shapes.

    Args:
        mask (np.ndarray): A 2D NumPy array representing the binary mask,
            where non-zero pixels indicate the segmented region.

    Returns:
        list[np.ndarray]: A list of polygons extracted from the mask.
            Each polygon is a NumPy array of shape (N, 2) with integer
            coordinates, where N is the number of points in the polygon.
    """
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)

    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    return [
        np.squeeze(contour, axis=1) for contour in contours if contour.shape[0] >= 3
    ]
