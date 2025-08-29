# Picsellia CV Engine

**Picsellia CV Engine** is a modular engine for building, testing, and deploying computer vision pipelines — fully integrated with the Picsellia platform.

Whether you're transforming datasets, training models, or tracking experiments, this engine helps you organize everything into **clean, reusable components**.

## 🧠 What’s a pipeline?

A pipeline is a structured sequence of actions — like:

- 🧼 Preprocessing images
- 🧪 Training a model
- 📊 Evaluating predictions
- ☁️ Uploading results to Picsellia

Each action is implemented as a step — a small, focused function decorated with @step.

You can chain together these steps inside a @pipeline, and run it locally or on Picsellia.

## 🚀 Getting Started

Install from PyPI:

- With uv:

```bash
uv add picsellia-cv-engine
uv add picsellia-pipelines-cli
```

 - With pip:

```bash
pip install picsellia-cv-engine
pip install picsellia-pipelines-cli
```

## 🛠 Create and run your first pipeline

Use the Picsellia Pipelines CLI to scaffold and manage your pipelines.

### 1. Initialize a pipeline

```bash
pxl-pipeline init my_pipeline --type training --template ultralytics
```
This generates everything you need: config, Dockerfile, code templates, and a virtual environment.

➡️ See [pipeline lifecycle and commands](https://picselliahq.github.io/picsellia-cv-engine/usage/cli_overview/)

### 2. Run it locally
```bash
pxl-pipeline test my_pipeline
```

### 3. Deploy to Picsellia

```bash
pxl-pipeline deploy my_pipeline
```

🔎 Want real examples?
Explore the [pipeline usage templates](https://picselliahq.github.io/picsellia-cv-engine/usage/) for training and processing workflows.

## 📘 Documentation

The full documentation is available at:
👉 https://picselliahq.github.io/picsellia-cv-engine/

It includes:

- Getting Started
- CLI Usage Guide
- API Reference
- Pipeline templates & examples

## 🧑‍💻 Local Development

To contribute or explore the code:

### 1. Clone the repo

```bash
git clone https://github.com/picselliahq/picsellia-cv-engine.git
cd picsellia-cv-engine
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the documentation

```bash
uv run mkdocs serve -a 127.0.0.1:8080
```
Then open http://127.0.0.1:8080 in your browser.
