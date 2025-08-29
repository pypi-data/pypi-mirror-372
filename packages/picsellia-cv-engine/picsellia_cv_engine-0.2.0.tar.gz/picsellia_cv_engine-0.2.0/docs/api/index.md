# 📖 API Reference

The **Picsellia CV Engine API** is a modular toolkit for building end-to-end pipelines. It’s organized into reusable components, decorators, and framework-specific extensions.

---

## Core concepts

- **Steps**: Modular units of logic (e.g. load, train, validate)
- **Pipelines**: Logical flows decorated with `@pipeline`, composed of `@step`
- **Contexts**: Injected objects carrying pipeline configuration and metadata

---

## Built-in components

### Base steps

#### Dataset
- [Loader](steps/base/dataset/loader.md)
- [Preprocessor](steps/base/dataset/preprocessor.md)
- [Uploader](steps/base/dataset/uploader.md)
- [Validator](steps/base/dataset/validator.md)

#### Model
- [Builder](steps/base/model/builder.md)
- [Evaluator](steps/base/model/evaluator.md)

#### Datalake
- [Loader](steps/base/datalake/loader.md)

---

## Framework-Specific extensions

Frameworks are isolated under: `src/picsellia_cv_engine/frameworks/<framework_name>/`


Each framework can include:

- Custom [model modules](frameworks/ultralytics/model/model.md)
- [Hyperparameter definitions](frameworks/ultralytics/parameters/hyper_parameters.md)
- Training, evaluation, or export [services](frameworks/ultralytics/services/model/trainer.md)
- [Framework-specific steps](steps/ultralytics/model/trainer.md)

---

## Decorators

- [@pipeline](decorators/pipeline_decorator.md) – Defines a pipeline entrypoint
- [@step](decorators/step_decorator.md) – Marks a function as a step
- [Step Metadata](decorators/step_metadata.md)

---

## Data models

- [COCO Dataset](core/data/dataset/coco_dataset.md)
- [Dataset Collection](core/data/dataset/dataset_collection.md)
- [Datalake Collection](core/data/datalake/datalake_collection.md)

---

## Code example

```python
from picsellia_cv_engine.decorators.pipeline_decorator import pipeline
from picsellia_cv_engine.steps.base.dataset.loader import load_yolo_datasets

@pipeline
def my_pipeline():
    dataset = load_yolo_datasets()
    ...
```
