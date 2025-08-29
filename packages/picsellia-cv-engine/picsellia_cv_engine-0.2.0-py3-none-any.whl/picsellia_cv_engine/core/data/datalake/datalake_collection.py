import os

from .datalake import Datalake


class DatalakeCollection:
    def __init__(
        self,
        input_datalake: Datalake,
        output_datalake: Datalake,
    ):
        self.input = input_datalake
        self.output = output_datalake

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __iter__(self):
        return iter([self.input, self.output])

    def download_all(self, images_destination_dir):
        for datalake in self:
            datalake.download_data(
                destination_dir=os.path.join(images_destination_dir, datalake.name)
            )
