# 🧠 How the pxl-pipeline cli works

## 🚀 Pipeline lifecycle

- `init` → generate template
- `test` → runs the pipeline locally in `.venv/`
- `deploy` → builds & pushes Docker image + registers in Picsellia
- `smoke-test` → runs pipeline in a container before deploying

## 📂 Project structure

Here is a typical pipeline folder structure:

```
my_pipeline/
├── config.toml
├── pyproject.toml
├── uv.lock
├── Dockerfile

├── picsellia_pipeline.py
├── local_pipeline.py
├── steps.py
├── utils/
│ └── parameters.py

├── runs/
│ └── run1/
│ └── run_config.toml

└── .venv/
```


### Key files:

- **`config.toml`**
  Describes the pipeline metadata, entrypoint files, requirements file, and model metadata.
  ➕ This makes pipelines easily portable and shareable.

- **`pyproject.toml` / `uv.lock`**
  Managed by [`uv`](https://github.com/astral-sh/uv) to declare dependencies.
  You don’t need to manually install anything — just run the CLI.

- **`picsellia_pipeline.py`**
  Entrypoint when running on Picsellia (inside Docker).

- **`local_pipeline.py`**
  Entrypoint for running and testing the pipeline locally.

- **`steps.py`**
  Contains `@step`-decorated functions that define the logic of your pipeline.

- **`utils/parameters.py`**
  Contains the parameter class (`TrainingHyperParameters`, `ProcessingParameters`, etc.) used to extract configuration at runtime.

- **`.venv/`**
  Created automatically by the CLI when you run `pxl-pipeline test`.

## 🔐 Environment variables

The CLI requires:

```bash
PICSELLIA_API_TOKEN
PICSELLIA_ORGANIZATION_NAME
PICSELLIA_HOST  # optional, defaults to https://app.picsellia.com
```

They are:

- Prompted once during init, test, or deploy
- Saved in: `~/.config/picsellia/.env`
- Automatically loaded on future runs


You can:

- Manually edit that file
- Or override any value in the current terminal session with export VAR=...


## 🧰 Dependency management with uv

Each pipeline uses `uv` as the dependency manager. It handles package resolution and installation via `pyproject.toml`, without needing pip or poetry.

### 📦 What happens during pxl-pipeline test?

When you run:

```bash
pxl-pipeline test my_pipeline
```

The following is automatically done for you:

- `uv lock` resolves all dependencies and generates/updates `uv.lock`
- `uv sync`  installs packages into `.venv/` based on the lock file

You don't need to install or activate anything manually — the CLI ensures the right environment is built.

### ➕ Adding dependencies

To install a PyPI package:

```bash
uv add opencv-python --project my_pipeline
```

To add a Git-based package:

```bash
uv add git+https://github.com/picselliahq/picsellia-cv-engine.git --project my_pipeline
```

This updates the pyproject.toml and uv.lock files inside your pipeline folder.

💡 Tip: the `--project` flag ensures the package is added to the correct pipeline folder.

## 📁 How `runs/` work

Each test run creates a new directory under runs/:

```
├── runs/
│   ├── run1/
│   ├── run2/
│   └── run3/
│       └── run_config.toml
```

Inside each run folder:

- `run_config.toml` stores the parameters used for that run (e.g. `experiment_id`, `model_version_id`, etc.)
- The dataset and model will be downloaded into this folder
- Logs, annotations, and any outputs will be saved here

### Reusing configurations

- If a previous run exists, the CLI will prompt:

```bash
📝 Reuse previous config? experiment_id=... [Y/n]
```

- Choosing Y reuses the last config (but creates a new folder and re-downloads assets).

- Use the flag `--reuse-dir` to reuse the same directory and config, without downloading again.

## Working with pipeline parameters

### ➕ Adding a custom parameter

Each pipeline includes a `utils/parameters.py` file containing a parameter class that extracts and validates values from Picsellia metadata (experiment or processing).

#### 1. Locate your parameters file

```
my_pipeline/
├── utils/
│   └── parameters.py  ← edit this file
```

#### 2. Edit the parameter class
Inside `parameters.py`, you’ll find a class that inherits from:

- `Parameters` (for processing pipelines)

- `HyperParameters` (for training pipelines)

Add your new fields by calling `self.extract_parameter(...)` in the constructor.

```python
from picsellia_cv_engine.core.parameters import Parameters

class ProcessingParameters(Parameters):
    def __init__(self, log_data):
        super().__init__(log_data)

        # Add your custom parameters here 👇
        self.threshold = self.extract_parameter(
            keys=["threshold"],
            expected_type=float,
            default=0.5,
        )

        self.use_filter = self.extract_parameter(
            keys=["use_filter"],
            expected_type=bool,
            default=True,
        )
```

3. Link the class in `config.toml`

Make sure the class is declared in your pipeline’s `config.toml`:

```toml
[execution]
parameters_class = "utils/parameters.py:ProcessingParameters"
```

#### ✅ What you can define

Each parameter can include:

| Field          | Description                                                           |
|----------------|-----------------------------------------------------------------------|
| `keys`         | One or more fallback keys (e.g. `["lr", "learning_rate"]`)            |
| `expected_type`| Type validation (`int`, `float`, `bool`, `str`, `Optional[...]`)      |
| `default`      | Optional default value (or `...` to mark as required)                 |
| `range_value`  | Value bounds: `(min, max)` for numeric parameters                     |


Advanced use cases (enums, optional types, dynamic validation) are documented in the base Parameters class via extract_parameter(...).

## ✅ Summary

- Pipelines are self-contained and shareable via config.toml

- Dependencies are isolated and reproducible with uv

- CLI stores runs in runs/, with config and outputs

- Parameters are centralized and easy to extend

- You can deploy to Picsellia with `pxl-pipeline deploy ...`

For template-specific usage, see:

-  [Training - Ultralytics](training/ultralytics.md)

- [Processing - Pre-annotation](processing/pre_annotation.md)

- [Processing - Dataset version creation](processing/dataset_version_creation.md)
