import os

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import Datalake, DatalakeCollection
from picsellia_cv_engine.core.contexts import PicselliaDatalakeProcessingContext


@step
def load_datalake() -> Datalake | DatalakeCollection:
    """
    Loads and prepares data from a Picsellia Datalake.

    This function retrieves **input and output datalakes** from an active **processing job**
    and downloads all associated data (e.g., images). It supports both **single datalake extraction**
    (input only) and **dual datalake extraction** (input & output).

    Usage:
    - Extracts **one or two datalakes** from the active **processing job**.
    - Downloads all associated data and organizes them into a structured object.
    - Ideal for **data processing tasks requiring images from a Datalake**.

    Behavior:
    - If only an **input datalake** is available, it downloads and returns `Datalake`.
    - If both **input and output datalakes** exist, it returns a `DatalakeCollection`,
      allowing access to both datasets.

    Requirements:
    - The **processing job** must have at least one attached datalake.
    - Ensure `job_id` is set in the active **processing context**.
    - Data assets should be **stored in the Picsellia Datalake**.

    Returns:
        - `Datalake`: If only an **input datalake** is available.
        - `DatalakeCollection`: If both **input and output datalakes** exist.

    Example:
    ```python
    from picsellia_cv_engine.steps.data_extraction.processing.datalake import load_datalake

    # Load datalake data from the active processing job
    datalake_data = load_datalake()

    # Check if the function returned a single datalake or a collection
    if isinstance(datalake_data, DatalakeCollection):
       logger.info("Using both input and output datalakes.")
       logger.info(f"Input datalake images: {datalake_data.input.image_dir}")
       logger.info(f"Output datalake images: {datalake_data.output.image_dir}")
    else:
       logger.info("Using only input datalake.")
       logger.info(f"Input datalake images: {datalake_data.image_dir}")
    ```
    """
    context: PicselliaDatalakeProcessingContext = Pipeline.get_active_context()
    input_datalake = Datalake(
        name="input",
        datalake=context.input_datalake,
        data_ids=context.data_ids,
        use_id=context.use_id,
    )
    if context.output_datalake:
        output_datalake = Datalake(
            name="output",
            datalake=context.output_datalake,
            use_id=context.use_id,
        )
        datalake_collection = DatalakeCollection(
            input_datalake=input_datalake,
            output_datalake=output_datalake,
        )
        datalake_collection.download_all(
            images_destination_dir=os.path.join(context.working_dir, "images")
        )
        return datalake_collection
    else:
        input_datalake.download_data(
            destination_dir=os.path.join(context.working_dir, "images")
        )
        return input_datalake
