# -*- coding: UTF-8 -*-
"""
Created on 26.04.23

Module with validators for configuration attributes.

:author:     Martin Dočekal
"""

import math
import os
from typing import Any, Optional, Iterable, Type, Callable, Collection

from classconfig.base import Validator


class AllValidator(Validator):
    """
    Combination of validators.

    applies all validators in given order:
        v1 -> v2 -> v3
    every must by ok
    """

    def __init__(self, validators: Iterable[Callable[[Any], bool]]):
        """
        Initialization of all validator.

        :param validators: validators that should be used
        """

        self.validators = validators

    def __call__(self, for_validation: Any):
        res = True
        for v in self.validators:
            res &= v(for_validation)
            if not res:
                break

        return res


class AnyValidator(Validator):
    """
    Combination of validators.

    applies all validators in given order:
        v1 -> v2 -> v3
    at least one must be ok
    """

    def __init__(self, validators: Iterable[Callable[[Any], Any]]):
        """
        Initialization of any validator.

        :param validators: validators that should be used
            a validator is a callable that will  raise exception for invalid input
        """

        self.validators = validators

    def __call__(self, for_validation: Any):
        all_e_msg = []
        for v in self.validators:
            try:
                if v(for_validation):
                    return True
            except Exception as e:
                all_e_msg.append(str(e))

        raise ValueError("\n".join(all_e_msg))


class TypeValidator(Validator):
    """
    Assures that the value is of given type.
    """
    TYPE: Type = object  #: type used as parameter of isinstance method used for check
    TYPE_NAME: Optional[str] = None  #: name of type used for exception message, by default is used class name of TYPE

    def __init__(self, t: Optional[Type] = None):
        """
        initialization of type validator

        :param t: type that should override the default one
        """
        if t is not None:
            self.TYPE = t

    def __call__(self, for_validation: Any):
        if not isinstance(for_validation, self.TYPE):
            raise TypeError(f"The value {for_validation} is not {self.TYPE.__name__}.")

        return True


class IntegerValidator(TypeValidator):
    """
    Assures that the value is an integer.
    """
    TYPE = int
    TYPE_NAME = "integer"


class FloatValidator(TypeValidator):
    """
    Assures that the value is a float.
    """
    TYPE = float
    TYPE_NAME = "float"


class StringValidator(TypeValidator):
    """
    Assures that the value is a string.
    """
    TYPE = str
    TYPE_NAME = "string"


class BoolValidator(TypeValidator):
    """
    Assures that the value is a boolean.
    """
    TYPE = bool
    TYPE_NAME = "boolean"


class MinValueIntegerValidator(IntegerValidator):
    """
    Assures that the value is an integer greater or equal given value.
    """

    def __init__(self, min_value: int):
        """
        init of validator

        :param min_value: the integer must be greater or equal to this value
        """
        super().__init__()
        self.min_value = min_value

    def __call__(self, for_validation: int):
        super().__call__(for_validation)
        if for_validation < self.min_value:
            raise ValueError(f"The value {for_validation} is not at least {self.min_value}.")
        return True


class MinValueFloatValidator(FloatValidator):
    """
    Assures that the value is a float greater or equal given value.
    """

    def __init__(self, min_value: float):
        """
        init of validator

        :param min_value: the float must be greater or equal this value
        """
        self.min_value = min_value

    def __call__(self, for_validation: float):
        super().__call__(for_validation)
        if for_validation < self.min_value:
            raise ValueError(f"The value {for_validation} is not at least {self.min_value}.")
        return True


class ValueInIntervalIntegerValidator(IntegerValidator):
    """
    Assures that the value is an integer in given interval.
    """

    def __init__(self, min_value: float = -math.inf, max_value: float = math.inf):
        """
        init of validator

        :param min_value: the integer must be greater or equal to this value
        :param max_value: the integer must be smaller or equal to this value
        """
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, for_validation: int):
        super().__call__(for_validation)
        if not (self.min_value <= for_validation <= self.max_value):
            raise ValueError(f"The value {for_validation} is not in interval [{self.min_value}, {self.max_value}].")
        return True


class ValueInIntervalFloatValidator(FloatValidator):
    """
    Assures that the value is a float in given interval.
    """

    def __init__(self, min_value: float = -math.inf, max_value: float = math.inf,
                 left_inclusive: bool = True, right_inclusive: bool = True):
        """
        init of validator

        :param min_value: the float must be greater or equal to this value
        :param max_value: the float must be smaller or equal to this value
        :param left_inclusive: whether the interval contains min value
        :param right_inclusive: whether the interval contains max value
        """
        self.min_value = min_value
        self.max_value = max_value
        self.left_inclusive = left_inclusive
        self.right_inclusive = right_inclusive

    def __call__(self, for_validation: float):
        super().__call__(for_validation)
        if not (self.min_value < for_validation < self.max_value) and \
                (not self.left_inclusive or self.min_value != for_validation) and \
                (not self.right_inclusive or self.max_value != for_validation):
            raise ValueError(f"The value {for_validation} is not in interval [{self.min_value}, {self.max_value}].")
        return True


class IsNoneValidator(Validator):
    """
    Assures that the value is none.
    """

    def __call__(self, for_validation: None):
        if for_validation is not None:
            raise ValueError(f"The value {for_validation} is not None.")
        return True


class CollectionOfTypesValidator(Validator):
    """
    Class for non-empty Collection of given types attributes.
    """

    def __init__(self, c: Type[Collection], t: Type, type_name: Optional[str] = None, allow_none: bool = False,
                 value_validator: Optional[Callable[[Any], bool]] = None, allow_empty: bool = False):
        """
        init of validator

        :param c: collection that should be checked
        :param t: type that should be checked
        :param type_name: name of type that should be checked if None then t.__name__ is used
        :param allow_none: the type can also be none
        :param value_validator: Validator for values in list
        :param allow_empty: the list can be empty
        """
        self.c = c
        self.t = t
        self.type_name = self.t.__name__ if type_name is None else type_name
        self.allow_none = allow_none
        self.value_validator = value_validator
        self.allow_empty = allow_empty

    def __call__(self, for_validation: Collection):
        if not isinstance(for_validation, self.c) or (not self.allow_empty and len(for_validation) == 0):
            raise ValueError(f"Must be a non empty {self.c.__name__} of {self.type_name} types.")

        for x in for_validation:
            if not isinstance(x, self.t) and ((self.allow_none and x is not None) or not self.allow_none):
                raise ValueError(f"Must be a non empty {self.c.__name__} of {self.type_name} types.")
            if self.value_validator is not None:
                if not self.value_validator(x):
                    return False
        return True


class ListOfTypesValidator(CollectionOfTypesValidator):
    """
    Class for non-empty list of given types attributes.
    """

    def __init__(self, t: Type, type_name: Optional[str] = None, allow_none: bool = False,
                 value_validator: Optional[Callable[[Any], Any]] = None, allow_empty: bool = False):
        """
        init of validator

        :param t: type that should be checked
        :param type_name: name of type that should be checked if None then t.__name__ is used
        :param allow_none: the type can also be none
        :param value_validator: Validator for values in list
        :param allow_empty: the list can be empty
        """
        super().__init__(list, t, type_name, allow_none, value_validator, allow_empty)


class FilePathValidator(StringValidator):
    """
    Validates that the attribute is string defining valid path to an existing file.
    """

    def __call__(self, for_validation: str):
        super().__call__(for_validation)
        if not os.path.isfile(for_validation):
            raise ValueError(f"Must be valid path to existing file.")
        return True

