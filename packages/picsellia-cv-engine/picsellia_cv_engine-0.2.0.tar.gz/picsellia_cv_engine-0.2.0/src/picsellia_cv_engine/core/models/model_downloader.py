import os
import tarfile
import zipfile

from picsellia import ModelFile


class ModelDownloader:
    """
    Handles downloading and optional extraction of model files.
    """

    def download_and_process(self, model_file: ModelFile, destination_path: str) -> str:
        """
        Download a model file and extract it if compressed.

        Args:
            model_file (ModelFile): The file to download.
            destination_path (str): Target directory for the downloaded file.

        Returns:
            str: Path to the extracted or raw file.
        """
        os.makedirs(destination_path, exist_ok=True)
        file_path = os.path.join(destination_path, model_file.filename)
        model_file.download(destination_path)

        return self._unzip_if_needed(
            file_path=file_path, destination_path=destination_path
        )

    def _unzip_if_needed(self, file_path: str, destination_path: str) -> str:
        """
        Extract .tar or .zip files if needed.

        Args:
            file_path (str): Path to the downloaded file.
            destination_path (str): Where to extract contents.

        Returns:
            str: Path to extracted contents or original file.
        """
        if file_path.endswith(".tar"):
            with tarfile.open(file_path, "r:*") as tar:
                tar.extractall(path=destination_path)
            os.remove(file_path)
            return file_path[:-4]

        elif file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zipf:
                zipf.extractall(path=destination_path)
            os.remove(file_path)
            return file_path[:-4]

        return file_path
