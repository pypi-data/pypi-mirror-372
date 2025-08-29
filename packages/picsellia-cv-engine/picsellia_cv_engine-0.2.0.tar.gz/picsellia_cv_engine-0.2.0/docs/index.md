# 📌 Welcome to the Picsellia CV Engine Docs

**Picsellia CV Engine** is a modular toolkit for building, testing, and deploying computer vision pipelines — all fully integrated with [Picsellia](https://picsellia.com). Whether you're processing datasets, training models, or deploying experiments, this engine helps you structure everything in a clean, reusable way.


## 🧠 What’s a pipeline?

A **pipeline** is a sequence of steps that defines how data flows — from raw inputs to final results.

In **Picsellia CV Engine**, pipelines are used for both:

- **Training pipelines**:

    Load training datasets, configure a model, run training, log results and export weights.

- **Processing pipelines**:

    Clean or filter datasets, apply data augmentation, run inference for pre-annotation, or convert formats.

Each unit of work is a step — a standalone function decorated with @step. You can reuse, extend, or combine steps freely depending on your needs.
## ✨ Key features
- **Composable Steps** – Use or customize ready-made steps for common operations (loading data, training, etc.)
- **Training Pipelines** – Structure model training (e.g. Ultralytics YOLO) with built-in logic
- **Processing Pipelines** – Clean, transform, or validate datasets before use
- **Framework Extensions** – Support custom training libraries via a pluggable architecture
- **CLI Automation** – Use `pxl-pipeline` cli to scaffold, test, and deploy pipelines locally or on Picsellia

## 🚀 Get started
- 📦 [Installation Guide](installation.md) – Set up the engine and CLI
- 🛠 [Usage Guide](usage/index.md) – Build your first processing or training pipeline
- 📖 [API Reference](api/index.md) – Explore contexts, decorators, steps, and framework integrations

## 👋 New to Picsellia?

- Learn more about the [Picsellia platform](https://app.picsellia.com/signup)
- Docs for the core [Picsellia SDK](https://documentation.picsellia.com/docs/welcome)
- Reach out for support or contribution ideas!
