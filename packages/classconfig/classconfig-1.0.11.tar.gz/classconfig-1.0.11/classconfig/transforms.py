# -*- coding: UTF-8 -*-
"""
Created on 26.04.23

Module with transformers for configuration attributes.

:author:     Martin Dočekal
"""
import multiprocessing
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type, Sequence, Union, Callable

from classconfig.base import AttributeTransformer
from classconfig.classes import sub_cls_from_its_name


class TryTransforms(AttributeTransformer):
    """
    Tries all provided transforms in given order and stops when a transform is not raising an exception.

    WARNING: all exceptions are caught
    """

    def __init__(self, transforms: Sequence[AttributeTransformer]):
        """
        :param transforms: transforms that should be tried in givne order
        """
        self.transforms = transforms

    def __call__(self, x: Any) -> Any:
        for t in self.transforms:
            try:
                x = t(x)
                break
            except Exception:
                ...

        return x


class RelativePathTransformer(AttributeTransformer):
    """
    Transforms relative paths.

    :ivar base_path: all relative path will be relative to this
            If this attribute is None when transformed a runtime error is raised.
    """

    def __init__(self, base_path: Optional[str] = None, eval_counters: bool = False, allow_none: bool = False,
                 force_relative_prefix: bool = False):
        """
        init of transformer

        :param base_path: all relative path will be relative to this
            if you pass None it means that you are expecting that the base path will be set later, when configuration is
            validated, however if it will not be set then the path will not be transformed
        :param eval_counters: whether to evaluate counters in path
            counter is a string in form {variable_name} which will be replaced by
                variable_name_CNT where CNT is a counter that is the maximum + 1 of all existing folders/files in
                given directory. If there is no such directory then CNT is 0.
                variable name must match regex [a-zA-Z0-9_]+
        :param allow_none: whether the path can be None
        :param force_relative_prefix: whether to force relative prefix ("./" or "../") to consider path as relative
        """
        self.base_path = base_path
        self.eval_counters = eval_counters
        self.allow_none = allow_none
        self.force_relative_prefix = force_relative_prefix

    def __call__(self, path: Optional[str]) -> Optional[str]:
        if self.allow_none and path is None:
            return path

        if path is None:
            raise ValueError("Path cannot be None.")

        if self.base_path is None:
            return path

        if not os.path.isabs(path):
            if not self.force_relative_prefix or path.startswith("../") or path.startswith("./"):
                path = str(Path(self.base_path).joinpath(path).resolve())
        if self.eval_counters:
            path = self._eval_counters_in_path(path)

        return path

    def _eval_counters_in_path(self, path: str) -> str:
        """
        Evaluates counters in path.

        :param path: path to evaluate
        :return: path with evaluated counters
        """
        while True:
            match = re.search(r"\{([a-zA-Z0-9_]+)\}", path)
            if match is None:
                break
            var_name = match.group(1)
            parent_dir_of_variable = os.path.dirname(path[:match.start()])
            path = path.replace(match.group(0),
                                f"{var_name}_{self._get_counter_value(parent_dir_of_variable, var_name)}")

        return path

    def _get_counter_value(self, parent_dir_of_variable: str, var_name: str) -> int:
        """
        Gets counter value for variable in given directory.

        :param parent_dir_of_variable: directory where the variable is
        :param var_name: name of variable
        :return: counter value (the +1 is included)
        """
        if not os.path.isdir(parent_dir_of_variable):
            return 0

        counter = 0
        for f in os.listdir(parent_dir_of_variable):
            match = re.match(rf"{var_name}_(\d+)", f)
            if match is not None:
                counter = max(counter, int(match.group(1)) + 1)

        return counter


class CPUWorkersTransformer(AttributeTransformer):
    """
    Converts the number of cpu workers from user format to a program one.
    """

    def __call__(self, user_cpu_cnt: int) -> int:
        """
        Converts the number of workers in following way:
            All non-negative numbers remain the same.
            -1 is transformed to the number of cpu counts
            all other cause exception

        :param user_cpu_cnt: users input
        :return: number of workers
        :raise ValueError: when cnt is < -1
        """
        if user_cpu_cnt >= 0:
            return user_cpu_cnt

        if user_cpu_cnt == -1:
            return multiprocessing.cpu_count()

        raise ValueError("The cpu count is invalid. The value must be >=-1.")


class EnumTransformer(AttributeTransformer):
    """
    Transforms string representation of enum to enum.
    """

    def __init__(self, enum: Type[Enum]):
        """
        init of validator

        :param enum: for which enum it is
        """
        self.enum = enum

    def __call__(self, for_transform: Union[str, Enum]) -> Enum:
        if isinstance(for_transform, Enum) and for_transform.__class__ == self.enum:
            return for_transform
        return self.enum[for_transform]


class SubclassTransformer(AttributeTransformer):
    """
    Transforms string representation of subclass to subclass (also the class itself is allowed and all
    subclasses recursively).
    """

    def __init__(self, parent_cls: Type):
        """
        init of transformer

        :param parent_cls: for which class it is
        """
        self.parent_cls = parent_cls

    def __call__(self, for_transform: Union[str, Type]) -> Type:
        """
        Transforms string representation of a class to a class.

        :param for_transform: name of a class that is subclass of parent_cls
        :return: transformed class
        :raise ValueError: when the class is not subclass of parent_cls
        """

        return sub_cls_from_its_name(self.parent_cls, for_transform if isinstance(for_transform, str) else for_transform.__name__)


class TransformIfNotNone(AttributeTransformer):
    """
    Transforms value if it is not None.
    """

    def __init__(self, transformer: Callable[[Any], Any]):
        """
        init of transformer

        :param transformer: transformer to use
        """
        self.transformer = transformer

    def __call__(self, for_transform: Any) -> Any:
        """
        Transforms value if it is not None.

        :param for_transform: value to transform
        :return: transformed value
        """
        if for_transform is None:
            return for_transform

        return self.transformer(for_transform)

