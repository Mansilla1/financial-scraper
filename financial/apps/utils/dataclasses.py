from dataclasses import fields
from typing import Dict, Type, TypeVar

from django.db.models import Model


T = TypeVar("T")


def build_dataclass_from_model_instance(
    klass: Type[T], instance: "Model", **kwargs,
) -> T:
    """
    Receives a dataclass, a model instance and other dataclass fields and values
    that are not part of the model.
    """
    # Get the dataclass fields
    dataclass_field_names = set(f.name for f in fields(klass))

    # Exclude given properties
    dataclass_field_names -= kwargs.keys()

    _kwargs = {field: getattr(instance, field) for field in dataclass_field_names}
    _kwargs.update(kwargs)

    return klass(**_kwargs)


def build_dataclass_from_dict(klass: Type[T], data: Dict, **kwargs) -> T:
    """
    Returns a dataclass that is formed with the data sent in `data` as a dict. Important
    to note that only fields defined in the dataclass and contained in the dict will be added.
    """
    # Get the dataclass fields
    dataclass_field_names = dict(set((f.name, f.type) for f in fields(klass) if f.init))

    _kwargs = {
        field_name: data.get(field_name)
        for field_name, _ in dataclass_field_names.items()
    }

    kwargs = kwargs or {}
    _kwargs.update(kwargs)

    return klass(**_kwargs)
