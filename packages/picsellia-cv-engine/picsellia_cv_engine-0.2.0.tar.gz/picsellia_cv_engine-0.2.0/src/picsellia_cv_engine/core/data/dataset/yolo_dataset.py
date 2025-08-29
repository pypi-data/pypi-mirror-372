import logging
import os
import zipfile

from picsellia import DatasetVersion, Label
from picsellia.exceptions import NoDataError
from picsellia.sdk.asset import MultiAsset
from picsellia.types.enums import AnnotationFileType
from tqdm import tqdm

from picsellia_cv_engine.core.data.dataset.utils import remove_empty_directories

from .base_dataset import BaseDataset

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


class YoloDataset(BaseDataset):
    """
    A specialized dataset for handling YOLO-formatted annotations.

    This class provides methods to download, process, and unzip YOLO annotations in batches,
    making it easier to handle large datasets for object detection tasks.
    """

    def __init__(
        self,
        name: str,
        dataset_version: DatasetVersion,
        assets: MultiAsset | None = None,
        labelmap: dict[str, Label] | None = None,
    ):
        """
        Initialize the YOLO dataset.

        Args:
            name (str): The name of the dataset.
            dataset_version (DatasetVersion): The version of the dataset to work with.
            assets (Optional[MultiAsset]): Preloaded assets, if available.
            labelmap (Optional[Dict[str, Label]]): Mapping of labels for the dataset.
        """
        super().__init__(
            name=name,
            dataset_version=dataset_version,
            assets=assets,
            labelmap=labelmap,
        )

    def download_annotations(
        self, destination_dir: str, use_id: bool | None = True
    ) -> None:
        """
        Downloads YOLO annotations for the dataset in batches.

        This method retrieves YOLO annotation files in batches, unzips them, and saves the contents
        to the specified directory.

        Args:
            destination_dir (str): The directory where annotations will be saved.
            use_id (Optional[bool]): Whether to use asset IDs in file paths (default: True).

        Raises:
            FileNotFoundError: If the destination path does not exist or is invalid.
            Exception: If an error occurs during batch processing.
        """
        self.annotations_dir = destination_dir
        os.makedirs(self.annotations_dir, exist_ok=True)
        assets_to_download = self._determine_assets_source()

        with tqdm(desc="Downloading YOLO annotation batches", unit="assets") as pbar:
            self._process_batches(
                destination_path=self.annotations_dir,
                assets_to_download=assets_to_download,
                pbar=pbar,
                use_id=use_id,
            )

        logger.info(f"YOLO annotations downloaded to {self.annotations_dir}")

    def _determine_assets_source(self) -> MultiAsset | None:
        """
        Determine the source of assets (preloaded or fetched dynamically).

        Returns:
            Optional[MultiAsset]: Preloaded assets if available, otherwise None for dynamic fetching.
        """
        if self.assets:
            logger.info("Using preloaded assets for batch download.")
            return self.assets
        else:
            logger.info(
                "Preloaded assets not available. Fetching assets incrementally."
            )
            return None

    def _process_batches(
        self,
        destination_path: str,
        assets_to_download: MultiAsset | None,
        pbar: tqdm,
        use_id: bool | None = True,
    ) -> None:
        """
        Process the assets in batches, exporting and unzipping YOLO annotations.

        Args:
            destination_path (str): The directory where annotations will be saved.
            use_id (bool): Whether to use asset IDs in file paths.
            assets_to_download (Optional[MultiAsset]): Preloaded assets or None for dynamic fetching.
            pbar (tqdm.tqdm): Progress bar instance.
        """
        offset = 0
        batch_index = 0

        while True:
            try:
                batch_assets = self._get_next_batch(
                    assets_to_download=assets_to_download, offset=offset
                )
                if not batch_assets:
                    logger.info("All assets have been processed.")
                    break

                yolo_annotation_path = self._export_batch(
                    batch_assets=batch_assets,
                    destination_path=destination_path,
                    use_id=use_id,
                )
                self.unzip(
                    zip_path=yolo_annotation_path, destination_path=destination_path
                )

                pbar.update(len(batch_assets))
                offset += len(batch_assets)
                batch_index += 1
            except NoDataError:
                logger.info("No more assets available to process. Exiting.")
                break
            except Exception as e:
                logger.error(
                    f"An error occurred during batch {batch_index} processing: {e}"
                )
                break

    def _get_next_batch(
        self, assets_to_download: MultiAsset | None, offset: int
    ) -> MultiAsset:
        """
        Fetch the next batch of assets.

        Args:
            assets_to_download (Optional[MultiAsset]): Preloaded assets or None for dynamic fetching.
            offset (int): Offset for the current batch.

        Returns:
            MultiAsset: The next batch of assets to process.
        """
        if assets_to_download:
            return assets_to_download[offset : offset + BATCH_SIZE]
        else:
            return self.get_assets_batch(limit=BATCH_SIZE, offset=offset)

    def _export_batch(
        self,
        batch_assets: MultiAsset,
        destination_path: str,
        use_id: bool | None = True,
    ) -> str:
        """
        Export YOLO annotations for a batch.

        Args:
            batch_assets (list): The assets for the current batch.
            destination_path (str): Path to save the exported ZIP file.
            use_id (bool): Whether to use asset IDs in file paths.

        Returns:
            str: The path to the exported YOLO annotation ZIP file.
        """
        yolo_annotation_path = self.dataset_version.export_annotation_file(
            annotation_file_type=AnnotationFileType.YOLO,
            target_path=destination_path,
            use_id=use_id,
            assets=batch_assets,
        )
        return yolo_annotation_path

    def unzip(self, zip_path: str, destination_path: str) -> None:
        """
        Extracts the contents of a ZIP file into the specified destination directory.

        This method removes the original ZIP file after extraction and cleans up any empty directories.

        Args:
            zip_path (str): The full path to the ZIP file.
            destination_path (str): The directory where the contents will be extracted.
        """
        if os.path.exists(zip_path):
            try:
                with zipfile.ZipFile(file=zip_path, mode="r") as zip_ref:
                    zip_ref.extractall(path=destination_path)
                os.remove(path=zip_path)
                remove_empty_directories(directory=destination_path)
                logger.info(
                    f"Successfully extracted {zip_path} into {destination_path}."
                )

            except zipfile.BadZipFile:
                logger.error(f"Failed to unzip {zip_path}: Bad ZIP file.")
            except Exception as e:
                logger.error(f"An error occurred while unzipping {zip_path}: {e}")
        else:
            logger.warning(f"ZIP file {zip_path} does not exist.")
