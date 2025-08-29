# Pre-Annotation Pipeline


This guide explains how to create, customize, test, and deploy a pre-annotation pipeline using `pxl-pipeline` cli with the `pre_annotation` template.

These pipelines apply an existing model (e.g. YOLOv8, GroundingDINO) to automatically annotate a dataset.

---
## **1. Initialize your pipeline**

```sh
pxl-pipeline init my_preannotation_pipeline --type processing --template pre_annotation
```

This generates a pipeline folder with standard files. See [project structure](../cli_overview.md#project-structure) for details.

## **2. Customize your pipeline**

### steps.py

Contains the `process()` step where the model is applied to the dataset.

```python
@step
def process(picsellia_model: Model, picsellia_dataset: CocoDataset):
    output_coco = process_images(
        picsellia_model=picsellia_model,
        picsellia_dataset=picsellia_dataset,
        parameters=parameters,
    )
    ...
    return picsellia_dataset
```

### utils/processing.py

Implements `process_images()` where you:

- Apply the model to each image
- Generate bounding boxes or segmentation masks
- Format the output in COCO

You can modify this logic to use a different model (e.g., GroundingDINO) or post-process detections.

### utils/parameters.py

Define your custom parameters (e.g. threshold):

```python
self.threshold = self.extract_parameter(["threshold"], expected_type=float, default=0.1)
```

Learn more in [Working with pipeline parameters](../cli_overview.md#working-with-pipeline-parameters).

## 3. Manage dependencies with `uv`

This template uses `uv` for dependency management.
Dependencies are declared in `pyproject.toml` and resolved automatically.

To add packages:

```bash
uv add opencv-python --project my_preannotation_pipeline
uv add git+https://github.com/picselliahq/picsellia-cv-engine.git --project my_preannotation_pipeline

```
See [dependency management with uv](../cli_overview.md#dependency-management-with-uv) for full details.

## 4. Test locally

```bash
pxl-pipeline test my_preannotation_pipeline
```

You’ll be prompted for:

- `input_dataset_version_id`
- `model_version_id`

A new folder will be created under `runs/`, storing config and results.

To reuse the same folder and avoid re-downloading assets, use:

```bash
pxl-pipeline test my_preannotation_pipeline --reuse-dir
```

See [how runs/ work](../cli_overview.md#how-runs-work) for more details.

## 5. Deploy to Picsellia

```bash
pxl-pipeline deploy my_preannotation_pipeline
```

This will:

- Build and push the Docker image

- Register the pipeline in Picsellia under **Processings → Dataset → Private**

See [deployment lifecycle](../cli_overview.md#pipeline-lifecycle).

Make sure you’re logged in to Docker before deploying.
