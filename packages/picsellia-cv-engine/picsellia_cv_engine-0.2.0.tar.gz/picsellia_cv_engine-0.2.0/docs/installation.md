# 📦 Installation

## Prerequisites
- Python **>=3.10**

## Install via PyPI

Use this option if you want to use the CV Engine and Pipeline CLI without modifying the code.


✅ With uv

```bash
uv pip install picsellia-cv-engine
uv pip install picsellia-pipelines-cli
```

✅ With pip

```bash
pip install picsellia-cv-engine
pip install picsellia-pipelines-cli
```

After that, the CLI is available as:

```bash
pxl-pipeline --help
```

## Develop Locally

Use this setup if you're contributing or exploring the codebase.

1. Clone the repository

```bash
git clone https://github.com/picselliahq/picsellia-cv-engine.git
cd picsellia-cv-engine
```

2. Install dependencies

```bash
uv sync
```

3. Serve the documentation locally (optional)

```bash
uv run mkdocs serve -a 127.0.0.1:8080
```

Then open http://127.0.0.1:8080 in your browser.
