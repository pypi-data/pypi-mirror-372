# -*- coding: UTF-8 -*-
"""
Created on 17.02.23
Base classes for configuration.

:author:     Martin Dočekal
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class Validator(ABC):
    """
    Base class for attributes validators
    """

    @abstractmethod
    def __call__(self, for_validation: Any):
        """
        Validates given input and raises exception for invalid one.

        :param for_validation: an input that should be checked
        :raise TypeError: when invalid type was provided
        :raise ValueError: when invalid value was provided
        """
        ...


class AttributeTransformer(ABC):
    """
    Transformer of user input to programming form.
    """

    @abstractmethod
    def __call__(self, for_transformation: Any) -> Any:
        """
        Transforms given user input and raises exception for invalid one.

        :param for_transformation: an input that should be transformed
        :raise TypeError: when invalid type was provided
        :raise ValueError: when invalid value was provided
        :raise RuntimeError: when a transformer is in invalid state
        :return: transformed value
        """
        ...


class ConfigurableAttribute(ABC):
    """
    Base class for configurable attribute that can be used for initialization from config file.
    Also, it can provide information to create a config file.
    """

    def __init__(self, desc: Optional[str] = None, name: Optional[str] = None, voluntary: bool = False,
                 hidden: bool = False):
        """
        Base class init with minimal required information for a user.

        :param desc: description of this attribute for user
        :param name: name of attribute that is suitable for user
        :param voluntary: If True this value might be missing in config and the default value will be used.
        :param hidden: If True this attribute will not be shown in config file.
            Is useful for attributes that are used for internal purposes, like passing the configuration itself.
        """
        self.desc = desc
        self.name = name
        self._member_name = None
        self.voluntary = voluntary
        self.hidden = hidden
        self.type = None

    def __set_name__(self, owner, name):
        self._member_name = name
        if self.name is None:
            self.name = name

        # get type of the attribute
        self.type = None
        if hasattr(owner, "__annotations__") and name in owner.__annotations__:
            self.type = owner.__annotations__[name]

    @property
    def member_name(self) -> str:
        """
        :return: name of the member that is used for this attribute
        """
        if self._member_name is None:
            raise RuntimeError("The member name is not set.")

        return self._member_name
