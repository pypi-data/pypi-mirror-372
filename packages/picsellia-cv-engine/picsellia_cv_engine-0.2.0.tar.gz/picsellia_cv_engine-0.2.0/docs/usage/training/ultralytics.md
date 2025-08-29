# Ultralytics Training Pipeline Template

This guide explains how to create, customize, test, and deploy a training pipeline using the `ultralytics` template from `pxl-pipeline` cli.

This pipeline integrates tightly with Picsellia for model logging, dataset handling, and experiment tracking.


## 1. Initialize your pipeline

```bash
pxl-pipeline init test_training --type training --template ultralytics
```

This generates a pipeline folder with standard files. See [project structure](../cli_overview.md#project-structure) for details.

During init, you'll be prompted to:

- Create a new model version or select an existing one
- If you create one, default parameters from `TrainingHyperParameters` will be used
- If using an existing model, ensure the parameter class matches the version's expected inputs

## 2. Customize your pipeline

### `steps.py`

This is where your model is built and trained:

```python
@step()
def train(picsellia_model: Model, picsellia_datasets: DatasetCollection[YoloDataset]):
    ...
```

You can modify:
- Preprocessing logic
- Model instantiation
- Training arguments
- Logging: save best model, export formats, etc.

### `utils/parameters.py`

This file defines the training configuration for the pipeline.

By default:

```python
class TrainingHyperParameters(HyperParameters):
    def __init__(self, log_data: LogDataType):
        super().__init__(log_data=log_data)
        self.epochs = self.extract_parameter(["epochs"], expected_type=int, default=3)
        self.batch_size = self.extract_parameter(["batch_size"], expected_type=int, default=8)
        self.image_size = self.extract_parameter(["image_size"], expected_type=int, default=640)

```

To add a new hyperparameter (e.g., learning rate):

```python
self.learning_rate = self.extract_parameter(["lr"], expected_type=float, default=0.001)
```

Use it in `steps.py`:

```python
ultralytics_model.train(
    ...,
    lr0=context.hyperparameters.learning_rate,
)
```

➡️ See [Working with pipeline parameters](../cli_overview.md#working-with-pipeline-parameters) for more advanced usage.

⚠️ Make sure your parameter class stays in sync with your model version’s expected configuration.
A sync feature will be added soon to help with this.

### `pyproject.toml`: Customize your dependencies

Dependencies are managed with uv.
To add a new package to the pipeline environment:

```bash
uv add albumentations --project test_training
```

To install a Git-based package:

```bash
uv add git+https://github.com/picselliahq/picsellia-cv-engine.git --project test_training
```

This updates the `pyproject.toml` and `uv.lock`.
The CLI will automatically install everything on the next test or deploy.

See [dependency management with uv](../cli_overview.md#dependency-management-with-uv) for full details.

## 3. Test your pipeline locally

```bash
pxl-pipeline test test_training
```

This will:

1. Create a `.venv` in the pipeline folder
2. Install dependencies using uv
3. Prompt for an `experiment_id`

You must create the experiment manually in the Picsellia UI and attach:

- The correct model version
- The training datasets

✅ Outputs will be saved under:

```python
pipelines/test_training/runs/<runX>/
├── run_config.toml
├── dataset/
└── models/
```

See [how runs/ work](../cli_overview.md#how-runs-work) for details on configuration reuse.

💡 If you update the parameters in TrainingHyperParameters, make sure to update them in the experiment config in the UI as well.

## 4. Deploy to Picsellia

```bash
pxl-pipeline deploy test_training
```

This will:

1. Build a Docker image (based on your Dockerfile)
2. Push it to your Docker registry
3. Register the pipeline with the selected model version in Picsellia

Your `Dockerfile` installs:

1. `picsellia-cv-engine`
2. Torch + CUDA (via pre-built wheels)
3. Any other dependencies from `pyproject.toml` or `requirements.txt`
