import logging
import os
from abc import abstractmethod
from typing import TypeVar

from picsellia import DatasetVersion, Label
from picsellia.exceptions import NoDataError
from picsellia.sdk.asset import MultiAsset

from picsellia_cv_engine.core.services.utils.dataset_logging import get_labelmap

logger = logging.getLogger(__name__)


class BaseDataset:
    """
    A base class to manage the context of a dataset, including metadata, paths,
    assets, and annotation management.

    This class provides methods to handle dataset assets and annotations, ensuring
    compatibility with the Picsellia SDK. Subclasses should implement the
    `download_annotations` method to manage annotation-specific logic.
    """

    def __init__(
        self,
        name: str,
        dataset_version: DatasetVersion,
        assets: MultiAsset | None = None,
        labelmap: dict[str, Label] | None = None,
    ):
        """
        Initializes a `BaseDataset` with the dataset's metadata and configuration.

        Args:
            name (str): The name of the dataset.
            dataset_version (DatasetVersion): The version of the dataset as managed by Picsellia.
            assets (Optional[MultiAsset]): A preloaded collection of assets. If not provided, assets
                will be listed dynamically as needed.
            labelmap (Optional[Dict[str, Label]]): A preloaded mapping of labels. If not provided,
                the labelmap will be fetched from the `DatasetVersion`.
        """
        self.name = name
        """The name of the dataset."""

        self.dataset_version = dataset_version
        """The version of the dataset from Picsellia."""

        self.assets = assets
        """A preloaded collection of assets. If not provided, assets will be dynamically listed."""

        if not labelmap:
            self.labelmap = get_labelmap(dataset_version=dataset_version)
        else:
            self.labelmap = labelmap or {}
        """A mapping of label names to Label objects used for annotations."""

        self.images_dir: str | None = None
        """The local directory where image assets are downloaded."""

        self.annotations_dir: str | None = None
        """The local directory where annotation files are stored."""

    @abstractmethod
    def download_annotations(
        self, destination_dir: str, use_id: bool | None = True
    ) -> None:
        """
        Abstract method to download annotations for the dataset.

        Subclasses must implement this method to define how annotations are retrieved
        and stored locally.

        Args:
            destination_dir (str): The directory where the annotations will be saved locally.
            use_id (Optional[bool]): If True, uses asset IDs for file naming. Defaults to True.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        pass

    def download_assets(
        self,
        destination_dir: str,
        use_id: bool | None = True,
        skip_asset_listing: bool | None = False,
    ) -> None:
        """
        Downloads all assets (e.g., images) associated with the dataset to the specified directory.

        This method retrieves and downloads all the assets linked to the dataset version.
        If assets are preloaded, they are directly downloaded; otherwise, the method dynamically
        lists and downloads them from the dataset version.

        Args:
            destination_dir (str): The directory where assets will be saved locally.
            use_id (Optional[bool]): If True, uses asset IDs to generate file paths. Defaults to True.
            skip_asset_listing (Optional[bool]): If True, skips listing assets after downloading.
                Defaults to False.

        Side Effects:
            - Creates the `destination_path` directory if it doesn't already exist.
            - Sets `self.images_dir` to the `destination_path`.

        Raises:
            NoDataError: If no assets are available for the dataset version.
        """
        os.makedirs(destination_dir, exist_ok=True)
        if self.assets:
            self.assets.download(target_path=str(destination_dir), use_id=use_id)
        else:
            try:
                self.dataset_version.download(
                    target_path=str(destination_dir), use_id=use_id
                )
            except NoDataError:
                logger.warning(
                    "No assets found in the dataset version, skipping asset download."
                )
            if not skip_asset_listing:
                try:
                    self.assets = self.dataset_version.list_assets()
                except NoDataError:
                    logger.warning(
                        "No assets found in the dataset version, skipping asset listing."
                    )
        self.images_dir = destination_dir

    def get_assets_batch(self, limit: int, offset: int) -> MultiAsset:
        """
        Retrieves a batch of assets from the dataset based on the specified limit and offset.

        This method is useful for processing large datasets in smaller chunks.

        Args:
            limit (int): The maximum number of assets to retrieve in the batch.
            offset (int): The starting index for asset retrieval.

        Returns:
            MultiAsset: A collection of assets retrieved from the dataset.

        Raises:
            NoDataError: If the offset exceeds the total number of assets in the dataset version.
        """
        return self.dataset_version.list_assets(limit=limit, offset=offset)


TBaseDataset = TypeVar("TBaseDataset", bound=BaseDataset)
