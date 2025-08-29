import logging
import os
from abc import ABC
from collections.abc import Iterator
from typing import Generic, TypeVar

from .base_dataset import BaseDataset

logger = logging.getLogger(__name__)


TBaseDataset = TypeVar("TBaseDataset", bound=BaseDataset)


class DatasetCollection(ABC, Generic[TBaseDataset]):
    """
    A collection of datasets for different splits of a dataset.

    This class aggregates datasets for the common splits used in machine learning projects:
    training, validation, and testing. It provides a convenient way to access and manipulate these
    datasets as a unified object. The class supports direct access to individual dataset
    contexts, iteration over all contexts, and collective operations on all contexts, such as downloading
    assets.
    """

    def __init__(self, datasets: list[TBaseDataset]):
        """
        Initializes the collection with a list of datasets.

        Args:
            datasets (List[TDataset]): A list of datasets for different splits (train, val, test).
        """
        self.datasets = {dataset.name: dataset for dataset in datasets}
        """A dictionary of datasets, indexed by their names."""

        self.dataset_path: str | None = None
        """The path to the dataset directory."""

    def __getitem__(self, key: str) -> TBaseDataset:
        """
        Retrieves a dataset by its name.

        Args:
            key (str): The name of the dataset.

        Returns:
            TDataset: The dataset corresponding to the given name.

        Raises:
            KeyError: If the provided key does not exist in the collection.
        """
        return self.datasets[key]

    def __setitem__(self, key: str, value: TBaseDataset):
        """
        Sets or updates a dataset in the collection.

        Args:
            key (str): The name of the dataset to update or add.
            value (TDataset): The dataset object to associate with the given name.
        """
        self.datasets[key] = value

    def __iter__(self) -> Iterator[TBaseDataset]:
        """
        Iterates over all datasets in the collection.

        Returns:
            Iterator[TDataset]: An iterator over the datasets.
        """
        return iter(self.datasets.values())

    def download_all(
        self,
        images_destination_dir: str,
        annotations_destination_dir: str,
        use_id: bool | None = True,
        skip_asset_listing: bool | None = False,
    ) -> None:
        """
        Downloads all assets and annotations for every dataset in the collection.

        For each dataset, this method:
        1. Downloads the assets (images) to the corresponding image directory.
        2. Downloads and builds the COCO annotation file for each dataset.

        Args:
            images_destination_dir (str): The directory where images will be saved.
            annotations_destination_dir (str): The directory where annotations will be saved.
            use_id (Optional[bool]): Whether to use asset IDs in the file paths. If None, the internal logic of each dataset will handle it.
            skip_asset_listing (bool, optional): If True, skips listing the assets when downloading. Defaults to False.

        Example:
            If you want to download assets and annotations for both train and validation datasets,
            this method will create two directories (e.g., `train/images`, `train/annotations`,
            `val/images`, `val/annotations`) under the specified `destination_path`.
        """
        for dataset in self:
            logger.info(f"Downloading assets for {dataset.name}")
            dataset.download_assets(
                destination_dir=os.path.join(images_destination_dir, dataset.name),
                use_id=use_id,
                skip_asset_listing=skip_asset_listing,
            )

            logger.info(f"Downloading annotations for {dataset.name}")
            dataset.download_annotations(
                destination_dir=os.path.join(annotations_destination_dir, dataset.name),
                use_id=use_id,
            )
