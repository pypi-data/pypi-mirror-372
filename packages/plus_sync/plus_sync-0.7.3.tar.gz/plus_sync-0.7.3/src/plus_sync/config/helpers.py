from typing import TYPE_CHECKING, Any, Callable

from attr import Attribute
from attrs import field
from attrs.validators import and_
from attrs_strict import type_validator

if TYPE_CHECKING:
    from plus_sync.config import Config


def validated_field(*args: Any, validator: Callable | None = None, **kwargs: Any) -> Any:
    validators = and_(type_validator(), validator) if validator else type_validator()

    return field(*args, validator=validators, **kwargs)


def validate_duplicate_names(instance: 'Config', attribute: Attribute, value: Any) -> None:
    all_names = instance.get_all_config_names()
    if not all_names:
        return
    if len(all_names) != len(set(all_names)):
        raise ValueError('Duplicate names are not allowed.')
