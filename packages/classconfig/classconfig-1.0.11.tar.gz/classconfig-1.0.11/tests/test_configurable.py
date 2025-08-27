# -*- coding: UTF-8 -*-
"""
Created on 10.11.22

:author:     Martin Dočekal
"""
import enum
import os
from dataclasses import field
from enum import Enum
from io import StringIO
from typing import Optional
from unittest import TestCase

from attr import dataclass

from classconfig import ConfigurableValue, ConfigurableFactory, Config, \
    ConfigurableMixin, DelayedFactory, ConfigurableSubclassFactory, \
    UsedConfig, LoadedConfig, ListOfConfigurableSubclassFactoryAttributes, ConfigError

from classconfig.transforms import EnumTransformer, TryTransforms, TransformIfNotNone
from classconfig.validators import TypeValidator, ValueInIntervalFloatValidator
from classconfig.yaml import YAML


class ClassWithConfAttributes:
    a: int = ConfigurableValue()
    b: Optional[str] = ConfigurableValue()


class TestConfigurableAttributeBaseMembers(TestCase):

    def test_base_members(self):
        self.assertEqual("a", ClassWithConfAttributes.a.name)
        self.assertEqual(None, ClassWithConfAttributes.a.desc)
        self.assertEqual(None, ClassWithConfAttributes.a.user_default)
        self.assertEqual(None, ClassWithConfAttributes.a.transform)
        self.assertEqual(None, ClassWithConfAttributes.a.validator)
        self.assertEqual(False, ClassWithConfAttributes.a.voluntary)
        self.assertEqual(False, ClassWithConfAttributes.a.hidden)
        self.assertEqual(int, ClassWithConfAttributes.a.type)

        self.assertEqual("b", ClassWithConfAttributes.b.name)
        self.assertEqual(None, ClassWithConfAttributes.b.desc)
        self.assertEqual(None, ClassWithConfAttributes.b.user_default)
        self.assertEqual(None, ClassWithConfAttributes.b.transform)
        self.assertEqual(None, ClassWithConfAttributes.b.validator)
        self.assertEqual(False, ClassWithConfAttributes.b.voluntary)
        self.assertEqual(False, ClassWithConfAttributes.b.hidden)
        self.assertEqual(Optional[str], ClassWithConfAttributes.b.type)
        # check optional in general

        self.assertEqual(str, ClassWithConfAttributes.b.type.__args__[0])


class BaseOfAnotherConfigurableClass:
    c = ConfigurableValue()


class AnotherConfigurableClass(BaseOfAnotherConfigurableClass):
    d = ConfigurableValue(desc="description of d", user_default="abc")

    def __init__(self, c: str, d: str):
        self.c = c
        self.d = d


class ParentC:
    ...


class ChildA(ParentC, ConfigurableMixin):
    child_a_attribute = ConfigurableValue()


class ChildB(ParentC, ConfigurableMixin):
    child_b_attribute = ConfigurableValue()
    another = ConfigurableFactory(desc="class that needs configuration", cls_type=AnotherConfigurableClass,
                                  voluntary=True)


class ChildC(ParentC, ConfigurableMixin):
    child_c_attribute = ConfigurableValue("child c attribute", user_default="abc")


class ListConfigurable(ConfigurableMixin):
    loggers = ListOfConfigurableSubclassFactoryAttributes(ConfigurableSubclassFactory(ParentC),
                                                          desc="list of loggers",
                                                          user_defaults=[ChildA, ChildA])


class Num(Enum):
    ONE = 1
    TWO = 2


class ConfigurableClass:
    config = UsedConfig()
    a = ConfigurableValue(name="arg", desc="description of a", user_default=1)
    another = ConfigurableFactory(desc="class that needs configuration", cls_type=AnotherConfigurableClass,
                                  voluntary=True)
    b = ConfigurableValue(desc="description of b", user_default="TWO", transform=EnumTransformer(Num),
                          validator=TypeValidator(Num), voluntary=True)

    parent = ConfigurableSubclassFactory(parent_cls_type=ParentC, desc="description of parent")
    parent_with_default = ConfigurableSubclassFactory(parent_cls_type=ParentC,
                                                      desc="description of parent_with_default", user_default=ChildB)

    loggers = ListOfConfigurableSubclassFactoryAttributes(ConfigurableSubclassFactory(ParentC),
                                                          desc="list of loggers",
                                                          user_defaults=[ChildA, ChildA])

    def __init__(self, config, a, another, b, parent, parent_with_default, loggers):
        self.config = config
        self.a = a
        self.another = another
        self.b = b
        self.parent = parent
        self.parent_with_default = parent_with_default
        self.loggers = loggers


class ConfigurableClassWithMixin(ConfigurableMixin):
    a = ConfigurableValue()
    b = ConfigurableValue()

    def __post_init__(self, b):
        self.c = b


class ConfigurableClassWithOmitHelper(ConfigurableMixin):
    a = ConfigurableValue()
    b = ConfigurableFactory(ChildB, desc="class that needs configuration")


class ConfigurableClassWithOmit(ConfigurableMixin):
    b = ConfigurableFactory(ConfigurableClassWithOmitHelper, desc="class that needs configuration", delay_init=True,
                            omit={
                                "": {ConfigurableClassWithOmitHelper.a.name},
                                "b": {
                                    "": ChildB.another.name
                                }
                            })


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
FIXTURES_PATH = os.path.join(SCRIPT_PATH, "fixtures")
CONFIG_PATH = os.path.join(FIXTURES_PATH, "config.yaml")
CONFIG_EXTRA_PATH = os.path.join(FIXTURES_PATH, "config_extra.yaml")
CONFIG_VOLUNTARY_MISSING_PATH = os.path.join(FIXTURES_PATH, "config_voluntary_missing.yaml")
CONFIG_OMIT_PATH = os.path.join(FIXTURES_PATH, "config_omit.yaml")


class TestConfigurableAttributes(TestCase):

    def test_no_type(self):
        class A(ConfigurableMixin):
            a = ConfigurableValue()

        self.assertIsNone(A.a.type)

    def test_type(self):
        class A(ConfigurableMixin):
            a: int = ConfigurableValue()

        self.assertEqual(int, A.a.type)


class TestDelayedFactory(TestCase):
    def setUp(self) -> None:
        self.factory = DelayedFactory(AnotherConfigurableClass, {"c": 2})

    def test_create(self):
        res = self.factory.create(d=5)
        self.assertEqual(2, res.c)
        self.assertEqual(5, res.d)


class TestConfigurableFactory(TestCase):
    def setUp(self) -> None:
        self.factory = ConfigurableFactory(ConfigurableClass)

    def test_create(self):
        config = LoadedConfig({
            "a": 1,
            "another": {
                "c": None,
                "d": "abc"
            },
            "b": Num.TWO,
            "parent": {
                "cls": "ChildA",
                "config": {
                    "child_a_attribute": 3
                }
            },
            "parent_with_default": {
                "cls": "ChildB",
                "config": {
                    "child_b_attribute": 4,
                    "another": {
                        "c": None,
                        "d": "cba"
                    },
                }
            },
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 5
                    }
                },
            ]
        })
        config.untransformed = config
        conf_cls = self.factory.create(config)
        self.assertTrue(isinstance(conf_cls, ConfigurableClass))
        self.assertEqual(config, conf_cls.config)
        self.assertEqual(1, conf_cls.a)
        self.assertTrue(isinstance(conf_cls.another, AnotherConfigurableClass))
        self.assertIsNone(conf_cls.another.c)
        self.assertEqual("abc", conf_cls.another.d)
        self.assertEqual(Num.TWO, conf_cls.b)
        self.assertTrue(isinstance(conf_cls.parent, ChildA))
        self.assertEqual(3, conf_cls.parent.child_a_attribute)
        self.assertTrue(isinstance(conf_cls.parent_with_default, ChildB))
        self.assertEqual(4, conf_cls.parent_with_default.child_b_attribute)
        self.assertTrue(isinstance(conf_cls.parent_with_default.another, AnotherConfigurableClass))
        self.assertIsNone(conf_cls.parent_with_default.another.c)
        self.assertEqual("cba", conf_cls.parent_with_default.another.d)
        self.assertEqual(1, len(conf_cls.loggers))
        self.assertTrue(isinstance(conf_cls.loggers[0], ChildA))
        self.assertEqual(5, conf_cls.loggers[0].child_a_attribute)


class TestDelayedConfigurableFactory(TestCase):
    def setUp(self) -> None:
        self.factory = ConfigurableFactory(ConfigurableClass, delay_init=True)

    def test_create(self):
        config = LoadedConfig({
            "a": 1,
            "another": {
                "c": None,
                "d": "abc"
            },
            "b": Num.TWO,
            "parent": {
                "cls": "ChildA",
                "config": {
                    "child_a_attribute": 3
                }
            },
            "parent_with_default": {
                "cls": "ChildB",
                "config": {
                    "child_b_attribute": 4,
                    "another": {
                        "c": None,
                        "d": "cba"
                    },
                }
            },
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 5
                    }
                },
            ]
        })
        factory = self.factory.create(config)
        self.assertTrue(isinstance(factory, DelayedFactory))
        self.assertEqual(ConfigurableClass, factory.cls_type)

        self.assertEqual(1, factory.args["a"])
        self.assertIsNone(factory.args["another"].c)
        self.assertEqual("abc", factory.args["another"].d)
        self.assertEqual(Num.TWO, factory.args["b"])


class TestConfigurableWithMixinFactory(TestCase):
    def setUp(self) -> None:
        self.factory = ConfigurableFactory(ConfigurableClassWithMixin)

    def test_create(self):
        config = {
            "a": 1,
            "b": 2
        }

        conf_cls = self.factory.create(config)
        self.assertTrue(isinstance(conf_cls, ConfigurableClassWithMixin))
        self.assertEqual(1, conf_cls.a)
        self.assertEqual(2, conf_cls.b)
        self.assertEqual(2, conf_cls.c)


class TestConfig(TestCase):
    str_repr = "arg: 1  # description of a\n" \
               "another: # class that needs configuration\n" \
               "  c:\n" \
               "  d: abc  # description of d\n" \
               "b: TWO # description of b\n" \
               "parent: # description of parent\n" \
               "  cls:  # name of class that is subclass of ParentC\n" \
               "  config: # configuration for defined class\n" \
               "parent_with_default: # description of parent_with_default\n" \
               "  cls: ChildB  # name of class that is subclass of ParentC\n" \
               "  config: # configuration for defined class\n" \
               "    child_b_attribute:\n" \
               "    another:  # class that needs configuration\n" \
               "      c:\n" \
               "      d: abc  # description of d\n" \
               "loggers: # list of loggers\n" \
               "- cls: ChildA  # name of class that is subclass of ParentC\n" \
               "  config: # configuration for defined class\n" \
               "    child_a_attribute:\n" \
               "- cls: ChildA  # name of class that is subclass of ParentC\n" \
               "  config: # configuration for defined class\n" \
               "    child_a_attribute:\n"

    def setUp(self) -> None:
        self.config = Config(ConfigurableClass)

    def test_generate_yaml_config(self):
        config = self.config.generate_yaml_config()
        self.assertEqual(self.str_repr, YAML().dumps(config))

    def test_save(self):
        stream = StringIO()
        self.config.save(stream)
        self.assertEqual(self.str_repr, stream.getvalue())

    def test_load_yaml(self):
        config = self.config.load(CONFIG_PATH)

        self.assertEqual({
            "a": 1,
            "another": {
                "c": None,
                "d": "abc"
            },
            "b": Num.TWO,
            "parent": {
                "cls": "ChildA",
                "config": {
                    "child_a_attribute": 3
                }
            },
            "parent_with_default": {
                "cls": "ChildB",
                "config": {
                    "child_b_attribute": 4,
                    "another": {
                        "c": None,
                        "d": "cba"
                    },
                }
            },
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 5
                    }
                },
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 6
                    }
                }
            ]
        }, config)

    def test_load_yaml_extra(self):
        self.config.allow_extra = False
        with self.assertRaises(ConfigError):
            _ = self.config.load(CONFIG_EXTRA_PATH)

    def test_load_yaml_allow_extra(self):
        config = self.config.load(CONFIG_EXTRA_PATH)

        self.assertEqual({
            "a": 1,
            "another": {
                "c": None,
                "d": "abc"
            },
            "b": Num.TWO,
            "parent": {
                "cls": "ChildA",
                "config": {
                    "child_a_attribute": 3
                }
            },
            "parent_with_default": {
                "cls": "ChildB",
                "config": {
                    "child_b_attribute": 4,
                    "another": {
                        "c": None,
                        "d": "cba"
                    },
                }
            },
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 5
                    }
                },
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 6
                    }
                }
            ]
        }, config)

    def test_load_yaml_voluntary_missing(self):
        config = self.config.load(CONFIG_VOLUNTARY_MISSING_PATH)
        self.assertEqual({
            "a": 1,
            "another": None,
            "b": Num.TWO,
            "parent": {
                "cls": "ChildA",
                "config": {
                    "child_a_attribute": 3
                }
            },
            "parent_with_default": {
                "cls": "ChildB",
                "config": {
                    "child_b_attribute": 4,
                    "another": {
                        "c": None,
                        "d": "cba"
                    },
                }
            },
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 5
                    }
                },
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 6
                    }
                }
            ]
        }, config)


class InventoryAllDefault(ConfigurableMixin):
    size: int = ConfigurableValue(desc="Size of an inventory", user_default=10, validator=lambda x: x > 0, transform=lambda x: x + 1)
    parent = ConfigurableSubclassFactory(parent_cls_type=ParentC, desc="description of parent", voluntary=True)


class TestConfigurableMixinDefaultInit(TestCase):
    def test_all_default(self):
        inv = InventoryAllDefault()
        self.assertEqual(11, inv.size)
        self.assertIsNone(inv.parent)


class Inventory(ConfigurableMixin):
    size: int = ConfigurableValue(desc="Size of an inventory", user_default=10, validator=lambda x: x > 0)
    parent = ConfigurableSubclassFactory(parent_cls_type=ParentC, desc="description of parent")


class Character(ConfigurableMixin):
    lvl: int = ConfigurableValue(desc="Level of a character", user_default=1, validator=lambda x: x > 0)
    name: str = ConfigurableValue(desc="Name of a character")
    inventory: Inventory = ConfigurableFactory(desc="Character's inventory", cls_type=Inventory)


class TestConfigurableValuesForObject(TestCase):

    def setUp(self) -> None:
        self.configurable_object = Character(lvl=99,
                                             name="John",
                                             inventory=Inventory(size=666, parent=ChildA(child_a_attribute="abc")))

    def test_config_from_object(self):
        config = Config.config_from_object(self.configurable_object)
        self.assertEqual({
            "lvl": 99,
            "name": "John",
            "inventory": {
                "size": 666,
                "parent": {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": "abc"
                    }
                }
            }
        }, config.file_override_user_defaults)
        self.assertEqual(Character, config.cls_type)

    def test_configurable_values_from_object(self):
        vals = Config.configurable_values_from_object(self.configurable_object)
        self.assertEqual(
            {
                "lvl": 99,
                "name": "John",
                "inventory": {
                    "size": 666,
                    "parent": {
                        "cls": "ChildA",
                        "config": {
                            "child_a_attribute": "abc"
                        }
                    }
                }
            },
            vals
        )


class ConfigurableClassWithOverridenUserDefaults:
    a = ConfigurableValue(desc="description of a", user_default=1)
    another = ConfigurableFactory(desc="class that needs configuration", cls_type=AnotherConfigurableClass,
                                  voluntary=True, file_override_user_defaults={"d": "cba"})
    c = ConfigurableSubclassFactory(parent_cls_type=BaseOfAnotherConfigurableClass,
                                    desc="description of c", user_default=AnotherConfigurableClass,
                                    file_override_user_defaults={"c": "opk", "d": "lmn"})
    sub_config = ConfigurableFactory(desc="class that needs configuration", cls_type=ConfigurableClass,
                                     file_override_user_defaults={
                                         "a": 2,
                                         "another": {"d": "cba"},
                                         "parent_with_default": {
                                             "cls": ChildA,
                                             "config": {
                                                 "child_a_attribute": "test"
                                             }
                                         }
                                     })


class TestConfigWithOverridenUserDefaults(TestCase):

    def setUp(self) -> None:
        self.config = Config(ConfigurableClassWithOverridenUserDefaults)

    def test_generate_yaml_config(self):
        config = self.config.generate_yaml_config()
        self.assertEqual(
            "a: 1  # description of a\n"
            "another: # class that needs configuration\n"
            "  c:\n"
            "  d: cba  # description of d\n"
            "c: # description of c\n"
            "  cls: AnotherConfigurableClass  # name of class that is subclass of BaseOfAnotherConfigurableClass\n"
            "  config: # configuration for defined class\n"
            "    c: opk\n"
            "    d: lmn  # description of d\n"
            "sub_config: # class that needs configuration\n"
            "  arg: 2  # description of a\n"
            "  another: # class that needs configuration\n"
            "    c:\n"
            "    d: cba  # description of d\n"
            "  b: TWO # description of b\n"
            "  parent: # description of parent\n"
            "    cls:  # name of class that is subclass of ParentC\n"
            "    config: # configuration for defined class\n"
            "  parent_with_default: # description of parent_with_default\n"
            "    cls: ChildA  # name of class that is subclass of ParentC\n"
            "    config: # configuration for defined class\n"
            "      child_a_attribute: test\n"
            "  loggers: # list of loggers\n"
            "  - cls: ChildA  # name of class that is subclass of ParentC\n"
            "    config: # configuration for defined class\n"
            "      child_a_attribute:\n"
            "  - cls: ChildA  # name of class that is subclass of ParentC\n"
            "    config: # configuration for defined class\n"
            "      child_a_attribute:\n"
            , YAML().dumps(config))


class MockEnum(enum.Enum):
    NEGATIVE_ONE = "-1"
    ZERO = "0"


class MockEnumTwo(enum.Enum):
    NEGATIVE_ONE = "-1"
    ZERO = "0"


class MockEnumThree(enum.Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"


class TestTryTransforms(TestCase):

    def test_empty(self):
        t = TryTransforms([])
        self.assertEqual(-1, t(-1))

    def test_non_ok(self):
        t = TryTransforms([EnumTransformer(MockEnumThree), EnumTransformer(MockEnum)])
        self.assertEqual(-1, t(-1))

    def test_one_ok(self):
        t = TryTransforms([EnumTransformer(MockEnumThree), EnumTransformer(MockEnum)])
        self.assertEqual(MockEnum.NEGATIVE_ONE, t("NEGATIVE_ONE"))

    def test_multiple_ok(self):
        t = TryTransforms([EnumTransformer(MockEnumThree), EnumTransformer(MockEnum),
                           EnumTransformer(MockEnumTwo)])
        self.assertEqual(MockEnum.NEGATIVE_ONE, t("NEGATIVE_ONE"))


class TestValueInIntervalFloatValidator(TestCase):
    def test_in_interval_inclusive(self):
        f = ValueInIntervalFloatValidator(2.0, 5.0)
        with self.assertRaises(ValueError):
            f(1.0)
        f(2.0)
        f(3.0)
        f(4.5)
        f(5.0)
        with self.assertRaises(ValueError):
            f(5.01)

    def test_in_interval_exclusive(self):
        f = ValueInIntervalFloatValidator(2.0, 5.0, left_inclusive=False, right_inclusive=False)
        with self.assertRaises(ValueError):
            f(1.0)
        with self.assertRaises(ValueError):
            f(2.0)
        f(3.0)
        f(4.5)
        with self.assertRaises(ValueError):
            f(5.0)
        with self.assertRaises(ValueError):
            f(5.01)

    def test_in_interval_left_inclusive(self):
        f = ValueInIntervalFloatValidator(2.0, 5.0, right_inclusive=False)
        with self.assertRaises(ValueError):
            f(1.0)

        f(2.0)
        f(3.0)
        f(4.5)
        with self.assertRaises(ValueError):
            f(5.0)
        with self.assertRaises(ValueError):
            f(5.01)

    def test_in_interval_right_inclusive(self):
        f = ValueInIntervalFloatValidator(2.0, 5.0, left_inclusive=False)
        with self.assertRaises(ValueError):
            f(1.0)
        with self.assertRaises(ValueError):
            f(2.0)
        f(3.0)
        f(4.5)
        f(5.0)
        with self.assertRaises(ValueError):
            f(5.01)


class ClassUsingConfigurableMixin(ConfigurableMixin):
    a = ConfigurableValue(desc="description of a", user_default=1)
    another = ConfigurableValue(desc="description of another")
    b = ConfigurableValue(desc="description of b", user_default="TWO")


class ClassUsingConfigurableMixinUsingPostInit(ConfigurableMixin):
    a = ConfigurableValue(desc="description of a", user_default=1)
    another = ConfigurableValue(desc="description of another")
    b = ConfigurableValue(desc="description of b", user_default="TWO")

    def __post_init__(self):
        self.another = 2


class TestConfigurableMixin(TestCase):

    def test_all_without_post_init(self):
        config = ClassUsingConfigurableMixin(a=1, another=10, b="ONE")
        self.assertEqual(1, config.a)
        self.assertEqual(10, config.another)
        self.assertEqual("ONE", config.b)

    def test_without_default_without_post_init(self):
        config = ClassUsingConfigurableMixin(another=10)
        self.assertEqual(1, config.a)
        self.assertEqual(10, config.another)
        self.assertEqual("TWO", config.b)

    def test_all_with_post_init(self):
        config = ClassUsingConfigurableMixinUsingPostInit(a=1, another=10, b="ONE")
        self.assertEqual(1, config.a)
        self.assertEqual(2, config.another)
        self.assertEqual("ONE", config.b)


class TestConfigurableClassWithOmit(TestCase):

    def setUp(self) -> None:
        self.config = Config(ConfigurableClassWithOmit)

    def test_generate_yaml_config(self):
        config = self.config.generate_yaml_config()
        self.assertEqual(
            "b:  # class that needs configuration\n"
            "  b:  # class that needs configuration\n"
            "    child_b_attribute:\n"
            , YAML().dumps(config))

    def test_load_yaml(self):
        config = self.config.load(CONFIG_OMIT_PATH)
        self.assertEqual({
            "b": {
                "b": {
                    "child_b_attribute": 4
                }
            }
        }, config)


class TestConfigurableFactoryWithOmit(TestCase):
    def setUp(self) -> None:
        self.config = ConfigurableFactory(ConfigurableClassWithOmit)

    def test_create(self):
        d = LoadedConfig({
            "b": {
                "b": {
                    "child_b_attribute": 4
                }
            }
        })
        res = self.config.create(d)
        self.assertTrue(isinstance(res.b, DelayedFactory))
        self.assertEqual(ConfigurableClassWithOmitHelper, res.b.cls_type)

        self.assertTrue(isinstance(res.b.args["b"], DelayedFactory))
        self.assertEqual({"child_b_attribute": 4}, res.b.args["b"].args)
        self.assertEqual(ChildB, res.b.args["b"].cls_type)


class TestListOfConfigurableFactoryAttributes(TestCase):
    def setUp(self) -> None:
        self.config = ConfigurableFactory(ListConfigurable)

    def test_create(self):
        d = LoadedConfig({
            "loggers": [
                {
                    "cls": "ChildA",
                    "config": {
                        "child_a_attribute": 1
                    }
                },
                {
                    "cls": "ChildC",
                    "config": {
                        "child_c_attribute": "2"
                    }
                }
            ]
        })
        res = self.config.create(d)
        self.assertEqual(2, len(res.loggers))
        self.assertTrue(isinstance(res.loggers[0], ChildA))
        self.assertEqual(1, res.loggers[0].child_a_attribute)
        self.assertTrue(isinstance(res.loggers[1], ChildC))
        self.assertEqual("2", res.loggers[1].child_c_attribute)


class TestTransformIfNotNone(TestCase):
    def setUp(self) -> None:
        self.trans = TransformIfNotNone(lambda x: x + 1)

    def test_transform_if_not_none(self):
        self.assertIsNone(self.trans(None))
        self.assertEqual(2, self.trans(1))
