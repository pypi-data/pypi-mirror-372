import functools
import inspect
from typing import Annotated, Any, Callable

import attrs


def inject_attrs(cls: type) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        cls_attrs = attrs.fields(cls)
        new_params_with_defaults = dict()
        new_params_wo_defaults = dict()
        for attr in cls_attrs:
            annotation = attr.type
            if attr.metadata.get('typer_annotation'):
                annotation = Annotated[annotation, attr.metadata['typer_annotation']]
            if attr.default is not attrs.NOTHING:
                default = attr.default
                if isinstance(default, attrs.Factory):  # type: ignore
                    default = default.factory(cls) if default.takes_self else default.factory()
            else:
                default = inspect.Parameter.empty
            param = inspect.Parameter(
                name=attr.name,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=annotation,
            )

            if param.default is inspect.Parameter.empty:
                new_params_wo_defaults[attr.name] = param
            else:
                new_params_with_defaults[attr.name] = param

        new_params = {**new_params_wo_defaults, **new_params_with_defaults}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = cls(**kwargs)
            return func(instance)

        wrapper.__signature__ = sig.replace(parameters=list(new_params.values()))  # type: ignore
        return wrapper

    return decorator
