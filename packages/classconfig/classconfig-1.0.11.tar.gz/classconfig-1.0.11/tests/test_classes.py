# -*- coding: UTF-8 -*-
"""
Created on 17.02.23

:author:     Martin Dočekal
"""
import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from unittest import TestCase

from classconfig.configurable import ConfigurableValue, Config
from classconfig.classes import subclasses, sub_cls_from_its_name, ConfigurableDataclassMixin, dataclass_field_2_configurable_attribute
from classconfig import get_configurable_attributes, YAML, ConfigurableFactory


class A:
    pass


class B(A):
    val = ConfigurableValue()
    pass


class C(A):
    pass


class D(B):
    pass


class E(C):
    pass


class F(D):
    pass


class G(E):
    pass


class H(F):
    val = ConfigurableValue()
    pass


class BAbc(B, ABC):
    @abstractmethod
    def abc_method(self):
        pass


class BaseOfAnotherConfigurableClass:
    c = ConfigurableValue()


class AnotherConfigurableClass(BaseOfAnotherConfigurableClass):
    d = ConfigurableValue(desc="description of d", user_default="abc")

    def __init__(self, c: str, d: str):
        self.c = c
        self.d = d


class TestSubclasses(unittest.TestCase):
    def test_subclasses(self):
        self.assertEqual(set(subclasses(A)), {B, C, D, E, F, G, H})

    def test_subclasses_abstract(self):
        self.assertEqual(set(subclasses(A, abstract_ok=True)), {B, C, D, E, F, G, H, BAbc})

    def test_subclasses_configurable(self):
        self.assertEqual(set(subclasses(A, configurable_only=True)), {B, D, F, H})

    def test_subclasses_configurable_abstract(self):
        self.assertEqual(set(subclasses(A, abstract_ok=True, configurable_only=True)), {B, D, F, H, BAbc})


class TestSubClsFromItsName(unittest.TestCase):

    def test_sub_cls_from_its_name(self):
        self.assertEqual(sub_cls_from_its_name(A, "B"), B)
        self.assertEqual(sub_cls_from_its_name(A, "C"), C)
        self.assertEqual(sub_cls_from_its_name(A, "D"), D)
        self.assertEqual(sub_cls_from_its_name(A, "E"), E)
        self.assertEqual(sub_cls_from_its_name(A, "F"), F)
        self.assertEqual(sub_cls_from_its_name(A, "G"), G)
        self.assertEqual(sub_cls_from_its_name(A, "H"), H)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting")

    def test_sub_cls_from_its_name_abstract(self):
        self.assertEqual(sub_cls_from_its_name(A, "BAbc", abstract_ok=True), BAbc)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting", abstract_ok=True)


class TestGetConfigurableAttributes(unittest.TestCase):
    def test_get_configurable_attributes(self):
        configurables = {"c": AnotherConfigurableClass.c, "d": AnotherConfigurableClass.d}
        res = get_configurable_attributes(AnotherConfigurableClass)
        self.assertSequenceEqual(configurables, res)


class ConfigurableClassC:
    text: str = ConfigurableValue(desc="description of text", user_default="help")
    r = ConfigurableValue(desc="description of text", user_default="abc")

    def __init__(self, text: str, r: str):
        self.text = text
        self.r = r


@dataclass
class ConfigurableDataclassB(ConfigurableDataclassMixin):
    a: int = field(default=10, metadata={"desc": "description of a"})
    b: str = field(default="abc", metadata={"desc": "description of b"})


@dataclass
class ConfigurableDataclassA(ConfigurableDataclassMixin):
    conf_b: ConfigurableDataclassB = field(metadata={"desc": "description of c"})
    test_class: ConfigurableClassC = field(metadata={"desc": "description of test_class"})
    a: int = field(default=1, metadata={"desc": "description of a"})
    b: str = field(default="def", metadata={"desc": "description of b"})
    d: dict = field(default_factory=dict, metadata={"desc": "description of d"})
    _g: bool = field(init=False, default=False)


@dataclass
class ConfigurableDataclassAHelp(ConfigurableDataclassMixin):
    DESC_METADATA = "help"
    conf_b: ConfigurableDataclassB = field(metadata={"help": "description of c"})
    test_class: ConfigurableClassC = field(metadata={"help": "description of test_class"})
    a: int = field(default=1, metadata={"help": "description of a"})
    b: str = field(default="def", metadata={"help": "description of b"})
    d: dict = field(default_factory=dict, metadata={"help": "description of d"})

@dataclass
class FieldsForDataclassFieldConversion:
    int_non_default_no_desc: int = field()
    int_non_default_desc: int = field(metadata={"desc": "description of int"})
    str_non_default_no_desc: str = field()
    str_non_default_desc: str = field(metadata={"desc": "description of str"})
    dict_non_default_no_desc: dict = field()
    dict_non_default_desc: dict = field(metadata={"desc": "description of dict"})
    class_non_default_no_desc: ConfigurableClassC = field()
    class_non_default_desc: ConfigurableClassC = field(metadata={"desc": "description of class"})

    str_default_no_desc: str = field(default="abc")
    str_default_desc: str = field(default="abc", metadata={"desc": "description of str"})
    int_default_no_desc: int = field(default=10)
    int_default_desc: int = field(default=10, metadata={"desc": "description of int"})
    dict_default_no_desc: dict = field(default_factory=dict)
    dict_default_desc: dict = field(default_factory=dict, metadata={"desc": "description of dict"})


class TestDataclassField2ConfigurableAttribute(TestCase):

    def setUp(self):
        self.fields = {
            f.name: f for f in fields(FieldsForDataclassFieldConversion)
        }

    def test_int_non_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["int_non_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))

    def test_int_non_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["int_non_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual("description of int", x.desc)

    def test_int_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["int_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual(10, x.user_default)

    def test_int_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["int_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual(10, x.user_default)
        self.assertEqual("description of int", x.desc)

    def test_str_non_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["str_non_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))

    def test_str_non_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["str_non_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual("description of str", x.desc)

    def test_str_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["str_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual("abc", x.user_default)

    def test_str_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["str_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual("abc", x.user_default)
        self.assertEqual("description of str", x.desc)

    def test_dict_non_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["dict_non_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))

    def test_dict_non_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["dict_non_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual("description of dict", x.desc)

    def test_dict_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["dict_default_no_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual({}, x.user_default)

    def test_dict_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["dict_default_desc"])
        self.assertEqual(ConfigurableValue, type(x))
        self.assertEqual({}, x.user_default)
        self.assertEqual("description of dict", x.desc)

    def test_class_non_default_no_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["class_non_default_no_desc"])
        self.assertEqual(ConfigurableFactory, type(x))

    def test_class_non_default_desc(self):
        x = dataclass_field_2_configurable_attribute(self.fields["class_non_default_desc"])
        self.assertEqual(ConfigurableFactory, type(x))
        self.assertEqual("description of class", x.desc)


class TestConfigurableDataclassMixin(TestCase):
    def test_to_yaml(self):
        c = Config(ConfigurableDataclassA)
        config = c.generate_yaml_config()

        self.assertEqual(
            "conf_b:  # description of c\n"
            "  a: 10  # description of a\n"
            "  b: abc # description of b\n"
            "test_class: # description of test_class\n"
            "  text: help  # description of text\n"
            "  r: abc # description of text\n"
            "a: 1 # description of a\n"
            "b: def # description of b\n"
            "d: {} # description of d\n"
            , YAML().dumps(config)
        )

    def test_to_yaml_non_default_desc(self):
        c = Config(ConfigurableDataclassAHelp)
        config = c.generate_yaml_config()

        self.assertEqual(
            "conf_b:  # description of c\n"
            "  a: 10  # description of a\n"
            "  b: abc # description of b\n"
            "test_class: # description of test_class\n"
            "  text: help  # description of text\n"
            "  r: abc # description of text\n"
            "a: 1 # description of a\n"
            "b: def # description of b\n"
            "d: {} # description of d\n"
            , YAML().dumps(config)
        )

    def test_from_yaml(self):
        c = Config(ConfigurableDataclassA)
        config_dict = {
            "conf_b": {
                "a": 20,
                "b": "xyz"
            },
            "test_class": {
                "text": "new text",
                "r": "new r"
            },
            "a": 2,
            "b": "new b",
            "d": {
                "key": "value"
            }
        }
        config = c.trans_and_val(config_dict, None)

        o = ConfigurableFactory(ConfigurableDataclassA).create(config)

        self.assertEqual(20, o.conf_b.a)
        self.assertEqual("xyz", o.conf_b.b)
        self.assertEqual("new text", o.test_class.text)
        self.assertEqual("new r", o.test_class.r)
        self.assertEqual(2, o.a)
        self.assertEqual("new b", o.b)
        self.assertEqual({"key": "value"}, o.d)

