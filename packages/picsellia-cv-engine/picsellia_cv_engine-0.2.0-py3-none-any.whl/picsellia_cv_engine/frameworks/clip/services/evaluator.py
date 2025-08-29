import os
import random
from collections.abc import Sequence
from typing import Any

import cv2
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import umap
from picsellia import Experiment
from picsellia.types.enums import LogType
from sklearn.metrics import silhouette_score


def run_umap_dbscan_clustering(
    embeddings: np.ndarray,
    min_samples: int = 5,
    initial_eps_list: list[float] | None = None,
    fallback_eps_list: list[float] | None = None,
    default_eps: float = 0.3,
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Run UMAP dimensionality reduction followed by DBSCAN clustering with automatic eps search.
    """
    if initial_eps_list is None:
        initial_eps_list = [0.1, 0.2, 0.3, 0.5, 0.8]
    if fallback_eps_list is None:
        fallback_eps_list = [0.05, 0.15, 0.25, 0.35, 0.6, 1.0]

    reduced = reduce_dimensionality_umap(embeddings, n_components=2)

    best_eps = find_best_eps(reduced, initial_eps_list)
    if best_eps is None:
        print("⚠️ No clusters found in first pass. Retrying with extended eps...")
        best_eps = find_best_eps(reduced, fallback_eps_list)
    if best_eps is None:
        print(f"⚠️ Still no clusters found. Falling back to eps={default_eps}")
        best_eps = default_eps

    labels = apply_dbscan_clustering(
        reduced, dbscan_eps=best_eps, dbscan_min_samples=min_samples
    )

    return reduced, labels, best_eps


def save_clustering_visualizations(
    reduced_embeddings: np.ndarray,
    cluster_labels: np.ndarray,
    image_paths: list[str],
    results_dir: str,
    log_images: bool = True,
    experiment: Experiment | None = None,
) -> None:
    """
    Save clustering plots, cluster image grids, and outlier grids. Optionally logs them to an experiment.

    Args:
        reduced_embeddings: UMAP-reduced 2D embeddings.
        cluster_labels: DBSCAN-assigned cluster labels.
        image_paths: Corresponding image file paths.
        results_dir: Output directory for saved plots.
        log_images: Whether to log images via experiment.
        experiment: Experiment if logging is enabled.
    """
    os.makedirs(results_dir, exist_ok=True)

    save_clustering_plots(reduced_embeddings, cluster_labels, results_dir=results_dir)
    save_cluster_images_plot(image_paths, cluster_labels, results_dir=results_dir)
    save_outliers_images(image_paths, cluster_labels, results_dir=results_dir)

    if log_images and experiment is not None:
        for file in os.listdir(results_dir):
            if file.endswith(".png"):
                experiment.log(
                    name=f"clip-eval/{file}",
                    data=os.path.join(results_dir, file),
                    type=LogType.IMAGE,
                )


def generate_embeddings_from_results(
    image_batches: Sequence[list[str]],
    batch_results: Sequence[list[dict[str, Any]]],
) -> tuple[np.ndarray, list[str]]:
    """
    Combine image paths and embeddings from batched inference results.

    Args:
        image_batches: List of image path batches.
        batch_results: List of inference result batches.

    Returns:
        A tuple of (embeddings array, image path list).
    """
    all_embeddings = []
    all_paths = []
    for images, results in zip(image_batches, batch_results, strict=False):
        for img_path, result in zip(images, results, strict=False):
            all_embeddings.append(result["image_embedding"])
            all_paths.append(img_path)
    return np.array(all_embeddings), all_paths


def load_stored_embeddings(file_path: str) -> tuple[np.ndarray, list[str]]:
    """
    Load stored embeddings and image paths from a .npz file.

    Args:
        file_path: Path to the .npz file.

    Returns:
        Tuple of (embeddings array, image paths).
    """
    data = np.load(file_path, allow_pickle=True)
    return data["embeddings"], data["image_paths"]


def reduce_dimensionality_umap(embeddings: np.ndarray, n_components: int) -> np.ndarray:
    """
    Reduce embedding dimensionality using UMAP.

    Args:
        embeddings: High-dimensional embeddings.
        n_components: Target number of dimensions.

    Returns:
        UMAP-reduced embeddings.
    """
    reducer = umap.UMAP(n_components=n_components, random_state=42)
    reduced_embeddings = reducer.fit_transform(X=embeddings)
    return reduced_embeddings


def apply_dbscan_clustering(
    embeddings: np.ndarray, dbscan_eps: float, dbscan_min_samples: int
) -> np.ndarray:
    """
    Apply DBSCAN clustering on embeddings.

    Args:
        embeddings: 2D array of points to cluster.
        dbscan_eps: Epsilon parameter for DBSCAN.
        dbscan_min_samples: Minimum samples per cluster.

    Returns:
        Array of cluster labels.
    """
    dbscan = sklearn.cluster.DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples)
    labels = dbscan.fit_predict(embeddings)
    return labels


def save_clustering_plots(
    reduced_embeddings: np.ndarray, cluster_labels: np.ndarray, results_dir: str
):
    """
    Save annotated DBSCAN clustering plot.

    Args:
        reduced_embeddings: 2D UMAP-reduced embeddings.
        cluster_labels: Cluster labels for each point.
        results_dir: Directory to save the plot.
    """
    os.makedirs(results_dir, exist_ok=True)
    unique_clusters = np.unique(cluster_labels)
    plt.figure(figsize=(10, 6))

    for cluster in unique_clusters:
        indices = np.where(cluster_labels == cluster)[0]
        if cluster == -1:
            plt.scatter(
                reduced_embeddings[indices, 0],
                reduced_embeddings[indices, 1],
                c="gray",
                s=10,
                alpha=0.3,
                label="Outliers",
            )
        else:
            plt.scatter(
                reduced_embeddings[indices, 0],
                reduced_embeddings[indices, 1],
                label=f"Cluster {cluster}",
                s=30,
                alpha=0.7,
            )
            cluster_center = np.mean(reduced_embeddings[indices], axis=0)
            plt.text(
                cluster_center[0],
                cluster_center[1],
                str(cluster),
                fontsize=12,
                weight="bold",
                bbox={"facecolor": "white", "alpha": 0.6, "edgecolor": "black"},
            )

    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.title("DBSCAN Cluster Visualization")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.savefig(
        os.path.join(results_dir, "dbscan_clusters_annotated.png"), bbox_inches="tight"
    )
    plt.close()


def save_cluster_images_plot(
    image_paths: list[str],
    cluster_labels: np.ndarray,
    results_dir: str,
    max_images_per_cluster: int = 25,
    grid_size: tuple[int, int] = (5, 5),
) -> None:
    """
    Save a grid of images for each cluster.

    Args:
        image_paths: List of image file paths.
        cluster_labels: Cluster label for each image.
        results_dir: Directory to save plots.
        max_images_per_cluster: Maximum number of images per plot.
        grid_size: Size of the plot grid (rows, cols).
    """
    os.makedirs(results_dir, exist_ok=True)
    unique_clusters = np.unique(cluster_labels)

    for cluster in unique_clusters:
        if cluster == -1:
            continue

        indices = np.where(cluster_labels == cluster)[0]
        if len(indices) == 0:
            continue

        selected_indices = random.sample(
            list(indices), min(max_images_per_cluster, len(indices))
        )

        fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(10, 10))
        fig.suptitle(f"Cluster {cluster}", fontsize=14)

        for ax, idx in zip(axes.flatten(), selected_indices, strict=False):
            img = cv2.imread(image_paths[idx])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ax.imshow(img)
            ax.axis("off")

        for i in range(len(selected_indices), grid_size[0] * grid_size[1]):
            axes.flatten()[i].axis("off")

        plot_path = os.path.join(results_dir, f"cluster_{cluster}_plot.png")
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()


def save_outliers_images(
    image_paths: list[str],
    cluster_labels: np.ndarray,
    results_dir: str,
    max_images: int = 25,
    grid_size: tuple[int, int] = (5, 5),
) -> None:
    """
    Save a grid of images classified as outliers.

    Args:
        image_paths: List of image file paths.
        cluster_labels: Cluster label for each image.
        results_dir: Directory to save the output.
        max_images: Maximum number of outlier images to display.
        grid_size: Size of the output grid (rows, cols).
    """
    os.makedirs(results_dir, exist_ok=True)
    outliers_indices = np.where(cluster_labels == -1)[0]
    if len(outliers_indices) == 0:
        return

    num_images = min(len(outliers_indices), max_images)
    selected_indices = random.sample(list(outliers_indices), num_images)

    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(10, 10))
    fig.suptitle("DBSCAN Outliers", fontsize=14)

    valid_images = 0
    for ax, idx in zip(axes.flatten(), selected_indices, strict=False):
        image_path = str(image_paths[idx])
        img = cv2.imread(image_path)
        if img is None:
            ax.axis("off")
            continue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ax.imshow(img)
        ax.axis("off")
        valid_images += 1

    for i in range(valid_images, grid_size[0] * grid_size[1]):
        axes.flatten()[i].axis("off")

    outliers_path = os.path.join(results_dir, "outliers_images.png")
    plt.savefig(outliers_path, bbox_inches="tight")
    plt.close()


def find_best_eps(reduced: np.ndarray, eps_list: list[float]) -> float | None:
    """
    Find the best epsilon value for DBSCAN using silhouette score.

    Args:
        reduced: 2D array of reduced embeddings.
        eps_list: List of candidate epsilon values.

    Returns:
        The epsilon value with the highest silhouette score.
    """
    best_eps = None
    best_score = -1
    for eps in eps_list:
        db = sklearn.cluster.DBSCAN(eps=eps, min_samples=5).fit(reduced)
        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if n_clusters >= 2:
            score = silhouette_score(reduced, labels)
            if score > best_score:
                best_score = score
                best_eps = eps
    return best_eps
