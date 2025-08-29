from typing import TypeVar

from picsellia_cv_engine import Pipeline, step
from picsellia_cv_engine.core import Model
from picsellia_cv_engine.core.services.model.utils import build_model_impl

TModel = TypeVar("TModel", bound=Model)


@step
def build_model(
    model_cls: type[TModel] = Model,
    pretrained_weights_name: str | None = None,
    trained_weights_name: str | None = None,
    config_name: str | None = None,
    exported_weights_name: str | None = None,
) -> TModel:
    """
    Instantiate and initialize a model for training or inference.

    This step constructs a `Model` object using the provided model class and the currently active pipeline context.
    It supports initializing the model with various types of weights, such as pretrained, trained, or exported weights,
    and optionally includes a configuration file.

    The method also ensures that any required weight files are downloaded to the appropriate local directory
    as defined by the context.

    Args:
        model_cls (type[TModel], optional): The model class to instantiate. Defaults to the base `Model` class.
        pretrained_weights_name (str, optional): The name of pretrained weights to load into the model.
        trained_weights_name (str, optional): The name of previously trained weights to resume training or evaluate.
        config_name (str, optional): The name of the configuration file to initialize the model.
        exported_weights_name (str, optional): The name of exported weights used for inference or deployment.

    Returns:
        TModel: An initialized model instance with the appropriate weights loaded.

    Raises:
        ResourceNotFoundError: If no matching model version is found in the experiment context.
        IOError: If required weight files fail to download or are inaccessible.
    """

    context = Pipeline.get_active_context()
    return build_model_impl(
        context=context,
        model_cls=model_cls,
        pretrained_weights_name=pretrained_weights_name,
        trained_weights_name=trained_weights_name,
        config_name=config_name,
        exported_weights_name=exported_weights_name,
    )
