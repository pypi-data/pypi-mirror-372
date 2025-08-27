# -*- coding: UTF-8 -*-
"""
Created on 17.02.23
Module with utils for working with classes itself.

:author:     Martin Dočekal
"""
import inspect
from dataclasses import is_dataclass, fields, MISSING

from typing import Type, List, TypeVar, Dict, Optional

from classconfig.base import ConfigurableAttribute

T = TypeVar("T")


class ConfigurableDataclassMixin:
    """
    Mixin that marks dataclass as configurable class.
    """

    DESC_METADATA = "desc"   # metadata key for description


def is_configurable(cls: Type, dataclass_mixin: bool = True) -> bool:
    """
    Checks if given class is configurable.

    :param cls: class to check
    :param dataclass_mixin: By default when a dataclass inherits from ConfigurableDataclassMixin all
        fields are considered configurable. If you want to disable this behavior set this to False.
    :return: True if class is configurable, False otherwise
    """

    if dataclass_mixin and isinstance(cls, ConfigurableDataclassMixin) and is_dataclass(cls):
        return len(fields(cls)) > 0

    # check whether parent classes are configurable
    if hasattr(cls, "__bases__"):
        for base in cls.__bases__:
            if is_configurable(base, dataclass_mixin=dataclass_mixin):
                return True

    if hasattr(cls, "__dict__"):
        for v_name in vars(cls):
            v = getattr(cls, v_name)
            if isinstance(v, ConfigurableAttribute):
                return True

    return False


def subclasses(cls_type: Type[T], abstract_ok: bool = False, configurable_only: bool = False) -> List[Type[T]]:
    """
    Returns all subclasses of given class.

    :param cls_type: parent class
    :param abstract_ok: if True also abstract classes will be returned
    :param configurable_only: if True only classes that are configurable will be returned
        configurable class is such that has at least one configurable attribute
    :return: all subclasses of given class
    """
    res = []
    for sub_cls in cls_type.__subclasses__():
        if (abstract_ok or not inspect.isabstract(sub_cls)) and \
                (not configurable_only or is_configurable(sub_cls)):
            res.append(sub_cls)
        res.extend(subclasses(sub_cls, abstract_ok, configurable_only))
    return res


def sub_cls_from_its_name(parent_cls: Type[T], name: str, abstract_ok: bool = False) -> Type[T]:
    """
    Searches all subclasses of given classes (also the class itself) and returns class with given name.

    :param parent_cls: parent class whose subclasses should be searched
    :param name: name of searched subclass
    :param abstract_ok: if True also abstract classes will be returned
    :return: subclass of given name
    :raise: ValueError when name with given subclass doesn't exist
    """

    if name == parent_cls.__name__ and (abstract_ok or not inspect.isabstract(parent_cls)):
        return parent_cls

    for c in subclasses(parent_cls, abstract_ok=abstract_ok):
        if c.__name__ == name:
            return c

    raise ValueError(f"Invalid subclass name {name} for parent class {parent_cls}")


def dataclass_field_2_configurable_attribute(field, desc_metadata: str = "desc", voluntary: bool = True) -> ConfigurableAttribute:
    """
    Converts dataclass field to configurable attribute.

    :param field: dataclass field
    :param desc_metadata: metadata key for description
    :param voluntary: if True the attribute is voluntary
    :return: configurable attribute
    """
    from classconfig import ConfigurableFactory, ConfigurableValue
    if field.type is not None:
        if is_dataclass(field.type) or is_configurable(field.type):
            return ConfigurableFactory(
                cls_type=field.type,
                desc=field.metadata.get(desc_metadata, None),
                name=field.name,
                voluntary=voluntary
            )

    default = None
    if field.default is not MISSING:
        default = field.default
    elif field.default_factory is not MISSING:
        default = field.default_factory()

    return ConfigurableValue(
        desc=field.metadata.get(desc_metadata, None),
        name=field.name,
        user_default=default,
        voluntary=voluntary
    )


def get_configurable_attributes(c: Type, dataclass_mixin: bool = True, use_dataclass_fields: bool = False,
                                desc_metadata: Optional[str] = None) -> Dict[str, ConfigurableAttribute]:
    """
    For given class returns all configurable attributes. Also obtains these from parents recursively.

    :param c: class to search the annotations
    :param dataclass_mixin: By default when a dataclass inherits from ConfigurableDataclassMixin all
        fields are considered configurable. If you want to disable this behavior set this to False.
    :param use_dataclass_fields: if True dataclass fields are considered as configurable attributes
    :param desc_metadata: metadata key for description
    :return: dict with name as key, and the configurable attribute as value
    """

    use_dataclass_fields = use_dataclass_fields
    if not use_dataclass_fields and dataclass_mixin and issubclass(c, ConfigurableDataclassMixin):
        use_dataclass_fields = True
        desc_metadata = c.DESC_METADATA

    configurables = {}
    for base in c.__bases__:
        configurables.update(get_configurable_attributes(base, dataclass_mixin=dataclass_mixin,
                                                         use_dataclass_fields=use_dataclass_fields,
                                                         desc_metadata=desc_metadata))

    if use_dataclass_fields and is_dataclass(c):
        for f in fields(c):
            if f.init is not False:
                configurables[f.name] = dataclass_field_2_configurable_attribute(f, desc_metadata=desc_metadata)

    for v_name in vars(c):
        v = getattr(c, v_name)
        if isinstance(v, ConfigurableAttribute):
            configurables[v_name] = v

    return configurables
