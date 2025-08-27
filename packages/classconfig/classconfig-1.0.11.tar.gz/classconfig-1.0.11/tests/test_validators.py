# -*- coding: UTF-8 -*-
"""
Created on 27.04.23

:author:     Martin Dočekal
"""
import math
import os
from unittest import TestCase

from classconfig.validators import AllValidator, AnyValidator, TypeValidator, IntegerValidator, FloatValidator, \
    StringValidator, BoolValidator, MinValueIntegerValidator, MinValueFloatValidator, ValueInIntervalIntegerValidator, \
    ValueInIntervalFloatValidator, IsNoneValidator, CollectionOfTypesValidator, ListOfTypesValidator, FilePathValidator


class Test(TestCase):
    def test_all_validator(self):
        def v_exception(x):
            if x < 10:
                return True
            raise Exception("Exception")
        validator = AllValidator([lambda x: x > 0, v_exception])

        self.assertTrue(validator(1))
        self.assertFalse(validator(0))

        with self.assertRaises(Exception):
            validator(10)

    def test_any_validator(self):
        def v_exception(x):
            if x < 10:
                return True
            raise Exception("Exception")

        validator = AnyValidator([lambda x: x > 0, v_exception])

        self.assertTrue(validator(1))
        self.assertTrue(validator(0))

        with self.assertRaises(Exception):
            validator(math.nan)

    def test_type_validator(self):
        validator = TypeValidator(int)

        self.assertTrue(validator(1))
        with self.assertRaises(Exception):
            validator(1.0)

    def test_integer_validator(self):
        validator = IntegerValidator()

        self.assertTrue(validator(1))
        with self.assertRaises(Exception):
            validator(1.0)

    def test_float_validator(self):
        validator = FloatValidator()

        self.assertTrue(validator(1.0))
        with self.assertRaises(Exception):
            validator(1)

    def test_string_validator(self):
        validator = StringValidator()

        self.assertTrue(validator("1"))
        with self.assertRaises(Exception):
            validator(1)

    def test_bool_validator(self):
        validator = BoolValidator()

        self.assertTrue(validator(True))
        with self.assertRaises(Exception):
            validator(1)

    def test_min_value_integer_validator(self):
        validator = MinValueIntegerValidator(10)

        self.assertTrue(validator(10))
        with self.assertRaises(Exception):
            validator(9)

    def test_min_value_float_validator(self):
        validator = MinValueFloatValidator(10.0)

        self.assertTrue(validator(10.0))
        with self.assertRaises(Exception):
            validator(9.0)

        with self.assertRaises(Exception):
            validator(10)

    def test_value_in_interval_integer_validator(self):
        validator = ValueInIntervalIntegerValidator(10, 20)

        self.assertTrue(validator(10))
        self.assertTrue(validator(20))
        self.assertTrue(validator(15))

        with self.assertRaises(Exception):
            validator(9)

        with self.assertRaises(Exception):
            validator(21)

        with self.assertRaises(Exception):
            validator(10.0)

    def test_value_in_interval_float_validator(self):
        validator = ValueInIntervalFloatValidator(10.0, 20.0)

        self.assertTrue(validator(10.0))
        self.assertTrue(validator(20.0))
        self.assertTrue(validator(15.0))

        with self.assertRaises(Exception):
            validator(9.0)

        with self.assertRaises(Exception):
            validator(21.0)

        with self.assertRaises(Exception):
            validator(10)

    def test_is_none_validator(self):
        validator = IsNoneValidator()

        self.assertTrue(validator(None))
        with self.assertRaises(Exception):
            validator(1)

    def test_collection_of_types_validator(self):
        # non empty with nones
        validator = CollectionOfTypesValidator(list, int)

        self.assertTrue(validator([1, 2, 3]))
        with self.assertRaises(Exception):
            validator([1, 2, 3.0])

        with self.assertRaises(Exception):
            validator([1, 2, None])

        with self.assertRaises(Exception):
            validator([])

        with self.assertRaises(Exception):
            validator({1, 2})

        # allow empty
        validator = CollectionOfTypesValidator(list, int, allow_empty=True)

        self.assertTrue(validator([1, 2, 3]))
        self.assertTrue(validator([]))

        # non empty with nones
        validator = CollectionOfTypesValidator(list, int, allow_none=True)

        self.assertTrue(validator([1, 2, 3]))
        self.assertTrue(validator([None, 1]))

        # allow empty and nones
        validator = CollectionOfTypesValidator(list, int, allow_empty=True, allow_none=True)

        self.assertTrue(validator([1, 2, 3]))
        self.assertTrue(validator([None, 1]))
        self.assertTrue(validator([]))

        # use custom value_validator

        def custom_validator(x):
            if x < 10:
                return True
            raise Exception("Exception")

        validator = CollectionOfTypesValidator(list, int, value_validator=custom_validator)

        self.assertTrue(validator([1, 2, 3]))
        with self.assertRaises(Exception):
            validator([1, 2, 22])

    def test_list_of_types_validator(self):
        validator = ListOfTypesValidator(int)

        self.assertTrue(validator([1, 2, 3]))
        with self.assertRaises(Exception):
            validator([1, 2, 3.0])

    def test_file_path_validator(self):
        validator = FilePathValidator()

        self.assertTrue(validator(__file__))

        if os.path.isfile(__file__+"non_existing_file"):
            self.skipTest(f"File {__file__}non_existing_file that is used as non existing file actually exists.")

        with self.assertRaises(Exception):
            validator(__file__+"non_existing_file")

