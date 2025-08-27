# -*- coding: UTF-8 -*-
"""
Created on 27.04.23

:author:     Martin Dočekal
"""
import enum
import multiprocessing
from enum import Enum
from unittest import TestCase
from classconfig.transforms import TryTransforms, RelativePathTransformer, CPUWorkersTransformer, EnumTransformer, \
    SubclassTransformer, TransformIfNotNone


class Test(TestCase):
    def test_try_transforms(self):
        transformer = TryTransforms([int, float, str])

        self.assertEqual(1, transformer("1"))
        self.assertEqual(1.0, transformer("1.0"))
        self.assertEqual("a", transformer("a"))

    def test_relative_path_transformer(self):
        transformer = RelativePathTransformer(base_path="/")

        self.assertEqual("/file.txt", transformer("file.txt"))

        with self.assertRaises(ValueError):
            transformer(None)

        transformer = RelativePathTransformer(base_path="/", allow_none=True)
        self.assertIsNone(transformer(None))

    def test_cpuworkers_transformer(self):
        transformer = CPUWorkersTransformer()

        self.assertEqual(0, transformer(0))
        self.assertEqual(1, transformer(1))
        self.assertEqual(3, transformer(3))
        self.assertEqual(multiprocessing.cpu_count(), transformer(-1))

        with self.assertRaises(ValueError):
            transformer(-2)

    def test_enum_transformer(self):
        class Colors(Enum):
            GREEN = enum.auto()
            RED = enum.auto()
            BLUE = enum.auto()

        transformer = EnumTransformer(Colors)

        self.assertEqual(Colors.GREEN, transformer("GREEN"))
        self.assertEqual(Colors.RED, transformer("RED"))
        self.assertEqual(Colors.BLUE, transformer("BLUE"))

        with self.assertRaises(KeyError):
            transformer("YELLOW")

    def test_subclass_transformer(self):

        class A:
            pass

        class B(A):
            pass

        class C:
            pass

        transformer = SubclassTransformer(A)
        self.assertEqual(A, transformer(A))
        self.assertEqual(A, transformer("A"))

        self.assertEqual(B, transformer(B))
        self.assertEqual(B, transformer("B"))

        with self.assertRaises(ValueError):
            transformer(C)

        with self.assertRaises(ValueError):
            transformer("C")

    def test_transform_if_not_none(self):
        transformer = TransformIfNotNone(int)

        self.assertEqual(1, transformer("1"))
        self.assertIsNone(transformer(None))
