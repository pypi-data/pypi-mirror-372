# Dataset Version Creation Pipeline


This guide explains how to create, customize, test, and deploy a dataset processing pipeline using `pxl-pipeline` cli with the `dataset_version_creation` template.

These pipelines are typically used to modify images and annotations — for example, applying augmentations or filtering classes.

---

## **1. Initialize your pipeline**

```sh
pxl-pipeline init my_custom_pipeline --type processing --template dataset_version_creation
```

This generates a pipeline folder with standard files. See [project structure](../cli_overview.md#project-structure) for details.

## **2. Customize your pipeline logic**

### steps.py

The `process_images()` function defines the core logic. It takes input images and COCO annotations, applies transformations, and writes the output to new directories.

```python
from picsellia_cv_engine import step

@step()
def process_images(input_images_dir: str, input_coco: dict, output_images_dir: str, output_coco: dict, parameters: dict):
    # Modify images and annotations here
    ...
    return output_coco
```

You can split your logic into multiple steps if needed.

###  Input/output contract
Each dataset processing step uses these I/O conventions:

- `input_images_dir` – Folder with input images

- `input_coco` – COCO annotation dict for input dataset

- `parameters` – Dict of pipeline parameters (see Working with parameters)

- `output_images_dir` – Empty folder where processed images must be saved

- `output_coco` – Empty dict where modified annotations must be written

💡 You must fill both `output_images_dir` and `output_coco`. They are automatically uploaded by the CLI after the step completes.


### Image processing example

Save processed images like this:

```python
processed_img.save(os.path.join(output_images_dir, image_filename))
```

Update output_coco with metadata:

```python
output_coco["images"].append({
    "id": new_id,
    "file_name": image_filename,
    "width": processed_img.width,
    "height": processed_img.height,
})
```

Be sure to also update the "annotations" field.

### ✔️ Checklist:

- Process and save all images to output_images_dir

- Append image metadata to output_coco["images"]

- Copy and adapt annotations to output_coco["annotations"]


## 3. Define pipeline parameters

Parameters can be passed through the pipeline’s context. If you need custom ones, define them in `utils/parameters.py` using a class that inherits from Parameters:

```python
class ProcessingParameters(Parameters):
    def __init__(self, log_data):
        super().__init__(log_data)
        self.blur = self.extract_parameter(["blur"], expected_type=bool, default=False)
```

See [Working with pipeline parameters](../cli_overview.md#working-with-pipeline-parameters) for more.

## 4. Manage dependencies with uv

To add Python packages, use:

```bash
uv add opencv-python --project my_custom_pipeline
uv add git+https://github.com/picselliahq/picsellia-cv-engine.git --project my_custom_pipeline
```

Dependencies are declared in pyproject.toml.
You don’t need to activate or install manually — see [dependency management with uv](../cli_overview.md#dependency-management-with-uv).

## 5. Test your pipeline locally

Run your test with:

```sh
pxl-pipeline test my_custom_pipeline
```

This will:

- Prompt for the input dataset and output name
- Run the pipeline via local_pipeline.py
- Save everything under runs/runX/ (see How runs work)

To reuse the same folder and avoid re-downloading assets, use:

```bash
pxl-pipeline test my_custom_pipeline --reuse-dir
```

See [how runs/ work](../cli_overview.md#how-runs-work) for more details.

## **6. Deploy to pipeline**

```sh
pxl-pipeline deploy my_custom_pipeline
```

This will:

- Build and push the Docker image

- Register the pipeline in Picsellia under **Processings → Dataset → Private**

See [deployment lifecycle](../cli_overview.md#pipeline-lifecycle).

Make sure you’re logged in to Docker before deploying.
