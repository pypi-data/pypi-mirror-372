# -*- coding: UTF-8 -*-
""""
Created on 10.08.22

Module for configurable attributes.

:author:     Martin Dočekal
"""
import argparse
import copy
from contextlib import nullcontext
from inspect import signature
from pathlib import Path
from typing import Any, Optional, Type, List, Generic, TypeVar, Sequence, Dict, Union, Callable, AbstractSet, TextIO

from ruamel.yaml import CommentedMap, CommentedSeq

from classconfig.base import ConfigurableAttribute
from classconfig.classes import sub_cls_from_its_name, get_configurable_attributes
from classconfig.transforms import RelativePathTransformer
from classconfig.yaml import YAML


class LoadedConfig(dict):
    """
    Loaded validated and transformed configuration.
    """

    @property
    def untransformed(self) -> Optional[Dict[str, Any]]:
        """
        Returns untransformed configuration.
        """
        try:
            return self._untransformed
        except AttributeError:
            return None

    @untransformed.setter
    def untransformed(self, value: Dict[str, Any]):
        self._untransformed = value

    @property
    def parent_config(self) -> Optional["LoadedConfig"]:
        """
        Returns parent configuration. Parent configuration is a configuration that has this configuration as its part.
        Is none when it was not set, or it is root.
        """
        try:
            return self._parent_config
        except AttributeError:
            return None

    @parent_config.setter
    def parent_config(self, value: "LoadedConfig"):
        self._parent_config = value


C = TypeVar("C")


class ConfigurableValue(ConfigurableAttribute, Generic[C]):
    """
    Defines configurable value that itself doesn't need configuration.
    """

    def __init__(self, desc: Optional[str] = None, name: Optional[str] = None, user_default: Any = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 transform: Optional[Callable[[Any], Any]] = None, voluntary: bool = False):
        """
        Initialization of configurable attribute.

        :param desc: description of this attribute for user
        :param name: name of attribute that is suitable for user
            If None it will be obtained with __set_name__ method
        :param user_default: default value of this attribute that should be shown to user
        :param validator: validator that assures that a valid value is used (during configuration loading)
            by raising an exception if the value is invalid
        :param transform: transformation of USER INPUT, the transformation is done before validation, thus it can
            be used to transform input to valid form
        :param voluntary: If True this value might be missing in config and the default value will be used.
        """
        super().__init__(desc, name, voluntary)

        self.user_default = user_default
        self.validator = validator
        self.transform = transform


T = TypeVar("T")


class DelayedFactory(Generic[T]):
    """
    Factory for delayer initialization.
    """

    def __init__(self, cls_type: Type[T], args: Dict, recursive: bool = True, propagate_recursion: bool = True):
        """
        Initialization of factory for given type.

        :param cls_type: class for which this factory should be for
        :param args: already prepared arguments
        :param recursive: if True the delayed factories inside, will be also used for initialization
            take on mind that this is not propagated to the next level if propagate_recursion is False
        :param propagate_recursion: if True the recursive flag will be propagated to the next level
            the propagate_recursion is never propagated to the next level
        """
        self.cls_type = cls_type
        self.args = args
        self.recursive = recursive
        self.propagate_recursion = propagate_recursion

    def create(self, **additional_args) -> T:
        """
        Creates instance of given class.

        :param additional_args: additional arguments that will be used together with the already loaded ones
        :return: initialized class
        """
        all_args = self.args | additional_args

        if self.recursive:
            for k, v in all_args.items():
                if isinstance(v, DelayedFactory):
                    old_recursive = v.recursive
                    if self.propagate_recursion:
                        v.recursive = True

                    all_args[k] = v.create()

                    if self.propagate_recursion:
                        v.recursive = old_recursive

        return self.cls_type(**all_args)


class ConfigurableFactory(ConfigurableAttribute, Generic[T]):
    """
    Factory for all classes that could be initialized with configuration.
    """

    def __init__(self, cls_type: Type[T], desc: Optional[str] = None, name: Optional[str] = None,
                 delay_init: bool = False, voluntary: bool = False, file_override_user_defaults: Optional[Dict] = None,
                 omit: Optional[Dict[str, Union[AbstractSet, Dict]]] = None):
        """
        defines for which class this factory is for

        :param cls_type: class for which this factory should be for
        :param desc: description of this attribute for user
        :param name: name of attribute that is suitable for user
            If None it will be obtained with __set_name__ method
        :param delay_init: delays class initializations
            It means that the :method:`~ConfigurableFactory.create` returns just a factory with loaded configuration.
            Might be useful when a class could be "initialized" just partially with configuration
        :param voluntary: If True this value might be missing in config and the default value will be used.
        :param file_override_user_defaults: overrides default values of configurable attributes for generating
            configuration file. It is useful when the default value is not suitable for user in different context.
            It is not overriding the user_default attribute of configurable attribute.
        :param omit: omit these attributes from configuration file as it is expected that they will be provided
            programmatically for this reason the delay_init will be set to True if not None

            Use "" to address attributes that are directly in the class, otherwise use the name of the attribute to
            address attributes that are in the class that is defined in the attribute. Works recursively.

            E.g.:
            {
                "": {"batch_size"}
                "model": {"input_size"}
            }
            Will omit batch_size from the passed class and input_size attribute of model attribute.

        """

        super().__init__(desc, name, voluntary)
        self.cls_type = cls_type
        self.delay_init = delay_init or omit is not None
        self.file_override_user_defaults = file_override_user_defaults
        self.omit = omit

    @staticmethod
    def should_omit(var_name: str, omit: Optional[Dict[str, Union[AbstractSet, Dict]]]) -> bool:
        """
        Checks if given variable should be omitted from configuration file.

        :param var_name: name of variable to check
        :param omit: omit these attributes from configuration file as it is expected that they will be provided
        :return: True if the variable should be omitted
        """
        if omit is None:
            return False

        if "" in omit:
            if var_name in omit[""]:
                return True

        return False

    @staticmethod
    def merge_omits(omit_a: Optional[Dict[str, Dict]], omit_b: Optional[Dict[str, Dict]]) -> Optional[Dict[str, Dict]]:
        """
        Merges two omit dictionaries.

        :param omit_a: first omit dictionary
        :param omit_b: second omit dictionary will update the first one (NOT in place)
        :return: merged omit dictionary
        """
        if omit_a is None:
            return omit_b
        if omit_b is None:
            return omit_a

        return omit_a | omit_b

    def create(self, config: LoadedConfig[str, Any], omit: Optional[Dict[str, Union[AbstractSet, Dict]]] = None) \
            -> Union[T, DelayedFactory[T]]:
        """
        Creates instance of given class.

        :param config: configuration for initialization
        :param omit: omit these attributes when creating
            if not None the delay_init will be used
        :return: initialized class or factory for delayed initialization if delay_init is active
        """

        k_args = {}

        current_omit = self.merge_omits(self.omit, omit)

        for var_name, var in get_configurable_attributes(self.cls_type).items():
            if self.should_omit(var_name, current_omit):
                continue

            if isinstance(var, ConfigurableFactory) or isinstance(var, ConfigurableSubclassFactory) or \
                    isinstance(var, ListOfConfigurableSubclassFactoryAttributes):
                pass_omit = None
                if current_omit is not None and var_name in current_omit:
                    pass_omit = current_omit[var_name]
                var_config = config[var_name]
                if var_config is not None:
                    k_args[var_name] = var.create(var_config, omit=pass_omit)
            elif isinstance(var, ConfigurableValue):
                k_args[var_name] = config[var_name]
            elif isinstance(var, UsedConfig):
                c = config
                if var.from_top_lvl:
                    while c.parent_config is not None:
                        c = c.parent_config
                k_args[var_name] = c

        return DelayedFactory(self.cls_type, k_args) \
            if self.delay_init or current_omit is not None else self.cls_type(**k_args)


class ConfigurableSubclassFactory(ConfigurableAttribute, Generic[T]):
    """
    Factory that enables to create any configurable class that is subclass of given parent class.
    """

    def __init__(self, parent_cls_type: Type[T], desc: Optional[str] = None, name: Optional[str] = None,
                 user_default: Any = None, delay_init: bool = False, voluntary: bool = False,
                 file_override_user_defaults: Optional[Dict] = None,
                 omit: Optional[Dict[str, Union[AbstractSet, Dict]]] = None):
        """
        defines for which class this factory is for

        :param parent_cls_type: parent class whose subclasses should be accepted also the class itself is accepted
        :param desc: description of this attribute for user
        :param name: name of attribute that is suitable for user
            If None it will be obtained with __set_name__ method
        :param user_default: default class that will be shown to user
        :param delay_init: delays class initializations
            It means that the :method:`~ConfigurableFactory.create` returns just a factory with loaded configuration.
            Might be useful when a class could be "initialized" just partially with configuration
        :param voluntary: If True this value might be missing in config and the default value will be used.
        :param file_override_user_defaults: overrides default values of configurable attributes for generating
            configuration file. It is useful when the default value is not suitable for user in different context.
            It is not overriding the user_default attribute of configurable attribute.
        :param omit: omit these attributes from configuration file as it is expected that they will be provided
            programmatically for this reason the delay_init will be set to True if not None

            Use "" to address attributes that are directly in the class, otherwise use the name of the attribute to
            address attributes that are in the class that is defined in the attribute. Works recursively.

            E.g.:
            {
                "": {"batch_size"}
                "model": {"input_size"}
            }
            Will omit batch_size from the passed class and input_size attribute of model attribute.

        """

        super().__init__(desc, name, voluntary)
        self.parent_cls_type = parent_cls_type
        self.delay_init = delay_init or omit is not None
        self.user_default = user_default
        self.file_override_user_defaults = file_override_user_defaults
        self.omit = omit

    def create(self, config: LoadedConfig[str, Any], omit: Optional[Dict[str, Union[AbstractSet, Dict]]] = None) \
            -> Union[T, DelayedFactory[T]]:
        """
        Creates instance of given class.

        :param config: configuration for initialization
            It expects dictionary with:
                cls: defining class name
                config: defining class configuration
        :param omit: omit these attributes when creating
            if not None the delay_init will be used
        :return: initialized class or factory for delayed initialization of delay_init is active
        """

        if self.omit is not None and omit is not None:
            act_omit = self.omit | omit
        else:
            act_omit = self.omit if self.omit is not None else omit
        factory = ConfigurableFactory(sub_cls_from_its_name(self.parent_cls_type, config["cls"]), None, None,
                                      self.delay_init, self.voluntary, self.file_override_user_defaults, act_omit)
        return factory.create(config["config"])


class ListOfConfigurableSubclassFactoryAttributes(ConfigurableAttribute, Generic[T]):

    def __init__(self, configurable_subclass_factory: ConfigurableSubclassFactory,
                 desc: Optional[str] = None,
                 name: Optional[str] = None,
                 user_defaults: Optional[List[Type]] = None,
                 voluntary: bool = False):
        """
        defines for which attributes this list is for

        :param configurable_subclass_factory: the list will contain only attributes of this type
        :param desc: description of this attribute for user
        :param name: name of attribute that is suitable for user
            If None it will be obtained with __set_name__ method
        :param user_defaults: voluntary you can provide default classes that will be used to feed the list
            when generating configuration file
            the user_default in ConfigurableSubclassFactory will be ignored
        :param voluntary: If True this value might be missing in config and the default value will be used.
        """
        super().__init__(desc, name, voluntary)
        self.configurable_subclass_factory = configurable_subclass_factory
        self.user_defaults = user_defaults

    def create(self, config: Sequence[LoadedConfig[str, Any]],
               omit: Sequence[Optional[Dict[str, Union[AbstractSet, Dict]]]] = None) \
            -> List[Union[T, DelayedFactory[T]]]:
        """
        Creates instance of given class.

        :param config: configuration for initialization
            It expects list with configuration for each item
        :param omit: omit these attributes when creating
            if not None the delay_init will be used
        :return: initialized class or factory for delayed initialization of delay_init is active
        """
        if omit is None:
            omit = [None] * len(config)

        return [self.configurable_subclass_factory.create(c, o) for c, o in zip(config, omit)]


class UsedConfig(ConfigurableAttribute):
    """
    Configurable attribute that is used to store used configuration.
    It is not visible for user in config file.
    """

    def __init__(self, from_top_lvl: bool = False):
        """
        :param from_top_lvl: if true you are requesting to get the whole configuration that was used to initialize
            the program not just subconfiguration of the class that is using this attribute
        """
        super().__init__(None, None, True, True)
        self.from_top_lvl = from_top_lvl


class ConfigError(Exception):
    """
    Exception for configuration related issues.
    """

    def __init__(self, msg: str, attribute: Optional[List[str]]):
        """
        initialization of configuration errors.

        :param msg: error message
        :param attribute: path to attribute (in config tree) for which the error is related to
        """
        self.msg = msg
        self.attribute = attribute

    def __str__(self):
        if self.attribute is None:
            return self.msg
        return self.msg + "\t" + "".join(f"[{a}]" for a in self.attribute)


class Config:
    """
    Class for loading/generating configuration for a class.
    """

    def __init__(self, cls_type: Type, file_override_user_defaults: Optional[Dict] = None,
                 omit: Optional[Dict[str, Union[AbstractSet, Dict]]] = None, path_to: Optional[str] = None, allow_extra: bool = True):
        """
        defines for which class this factory is for

        :param cls_type: class for which this config is for
        :param file_override_user_defaults: overrides default values of configurable attributes for generating
            configuration file. It is useful when the default value is not suitable for user in different context.
            It is not overriding the user_default attribute of configurable attribute.
        :param omit: omit these attributes from configuration file as it is expected that they will be provided
            programmatically

            Use "" to address attributes that are directly in the class, otherwise use the name of the attribute to
            address attributes that are in the class that is defined in the attribute. Works recursively.

            E.g.:
            {
                "": {"batch_size"}
                "model": {"input_size"}
            }
            Will omit batch_size from the passed class and input_size attribute of model attribute.
        :param path_to: voluntary you can provide path to configuration file from which the configuration was loaded
            it will be used for transformation of relative paths
        :param allow_extra: if True extra attributes in configuration are allowed
        """

        self.cls_type = cls_type
        self.file_override_user_defaults = file_override_user_defaults
        self.omit = omit
        self.path_to = path_to
        self.arg_parser = self.create_arg_parser()
        self.allow_extra = allow_extra

    @staticmethod
    def pass_omit(omit: Optional[Dict[str, Union[AbstractSet, Dict]]], attribute_name: str,
                  attribute: ConfigurableAttribute) -> Optional[Dict[str, Union[AbstractSet, Dict]]]:
        """
        Omit that should be passed to deeper attributes.

        :param omit: current omit
        :param attribute_name: name of deeper attribute
        :param attribute: deeper attribute
        :return: omit that should be passed to deeper attributes
        """
        pass_omit = None
        if isinstance(attribute, ConfigurableFactory) or isinstance(attribute, ConfigurableSubclassFactory):
            if omit is not None and attribute_name in omit:
                pass_omit = omit[attribute_name]

            pass_omit = ConfigurableFactory.merge_omits(attribute.omit, pass_omit)

        return pass_omit

    def generate_yaml_for_configurable_factory(self, attribute_name: str, attribute: ConfigurableFactory,
                                               comments: bool) -> CommentedMap:
        """
        Generates yaml for configurable factory.

        :param attribute_name: name of attribute
        :param attribute: attribute
        :param comments: true inserts comments
        :return: yaml
        """
        return Config(
            attribute.cls_type, self._parse_file_override_user_defaults(attribute),
            omit=self.pass_omit(self.omit, attribute_name, attribute)
        ).generate_yaml_config(comments=comments)

    def generate_yaml_for_configurable_subclass_factory(self, attribute_name: str,
                                                        attribute: ConfigurableSubclassFactory,
                                                        comments: bool) -> CommentedMap:
        """
        Generates yaml for configurable subclass factory.

        :param attribute_name: name of attribute
        :param attribute: attribute
        :param comments: true inserts comments
        :return: yaml
        """
        yaml_sub_fac = CommentedMap()

        for_cls = None
        for_cls_config = None
        user_default = attribute.user_default
        if self.file_override_user_defaults is not None and attribute_name in self.file_override_user_defaults:
            user_default = self.file_override_user_defaults[attribute_name]
            user_default = user_default["cls"]

        if user_default is not None:
            if isinstance(user_default, str):
                user_default = sub_cls_from_its_name(attribute.parent_cls_type, user_default, abstract_ok=True)

            for_cls = user_default.__name__

            for_cls_config = Config(user_default, self._parse_file_override_user_defaults(attribute),
                                    omit=self.pass_omit(self.omit, attribute_name, attribute)) \
                .generate_yaml_config(comments=comments)

        yaml_sub_fac.insert(0, "cls", for_cls,
                            comment=f"name of class that is subclass of {attribute.parent_cls_type.__name__}")
        yaml_sub_fac.insert(1, "config", for_cls_config, f"configuration for defined class")

        return yaml_sub_fac

    def generate_yaml_for_configurable_value(self, attribute_name: str, attribute: ConfigurableValue) -> any:
        """
        Generates yaml for configurable value.

        :param attribute_name: name of attribute
        :param attribute: attribute
        :return: the value for config file
        """

        user_default = attribute.user_default
        if self.file_override_user_defaults is not None and attribute_name in self.file_override_user_defaults:
            user_default = self.file_override_user_defaults[attribute_name]

        return user_default

    def generate_yaml_for_list_of_configurable_factories(self,
                                                         attribute: ListOfConfigurableSubclassFactoryAttributes,
                                                         comments: bool) -> CommentedSeq:
        """
        Generates yaml for list of configurable factories.

        :param attribute_name: name of attribute
        :param attribute: attribute
        :param comments: true inserts comments
        :return: yaml
        """
        yaml_list = CommentedSeq()
        if attribute.user_defaults is not None:
            for j, d in enumerate(attribute.user_defaults):
                fact = copy.deepcopy(attribute.configurable_subclass_factory)
                fact.user_default = d
                yaml_list.insert(j, self.generate_yaml_for_configurable_subclass_factory("", fact, comments))

        return yaml_list

    def generate_yaml_config(self, comments: bool = True) -> CommentedMap:
        """
        Converts configuration into YAML.

        :param comments: true inserts comments
        :return: configuration in YAML format
        """

        yaml = CommentedMap()
        for i, (var_name, var) in enumerate(get_configurable_attributes(self.cls_type).items()):
            if ConfigurableFactory.should_omit(var_name, self.omit):
                continue

            if isinstance(var, ConfigurableFactory):
                generated = self.generate_yaml_for_configurable_factory(var_name, var, comments)
            elif isinstance(var, ConfigurableSubclassFactory):
                generated = self.generate_yaml_for_configurable_subclass_factory(var_name, var, comments)
            elif isinstance(var, ListOfConfigurableSubclassFactoryAttributes):
                generated = self.generate_yaml_for_list_of_configurable_factories(var, comments)
            elif isinstance(var, ConfigurableValue):
                generated = self.generate_yaml_for_configurable_value(var_name, var)
            elif isinstance(var, UsedConfig):
                continue
            else:
                raise ValueError(f"Unknown type {type(var)}")

            yaml.insert(i, var.name, generated, comment=var.desc if comments else None)

        return yaml

    @classmethod
    def config_from_object(cls, o: Any) -> "Config":
        """
        Creates configuration with user default values from given object.

        :param o: object with values
        :return: configuration
        """

        return Config(o.__class__, file_override_user_defaults=cls.configurable_values_from_object(o))

    @classmethod
    def configurable_values_from_object(cls, o: Any) -> Dict:
        """
        Creates dictionary with values associated for configurable attributes from given object.

        :param o: object with values
        :return: dictionary with user default values
        """
        config = {}

        for i, (var_name, var) in enumerate(get_configurable_attributes(o.__class__).items()):
            if isinstance(var, ConfigurableValue):
                config[var_name] = getattr(o, var_name)
            elif isinstance(var, ConfigurableFactory):
                config[var_name] = cls.configurable_values_from_object(getattr(o, var_name))
            elif isinstance(var, ConfigurableSubclassFactory):
                config[var_name] = {}
                config[var_name]["cls"] = getattr(o, var_name).__class__.__name__
                config[var_name]["config"] = cls.configurable_values_from_object(getattr(o, var_name))
            elif isinstance(var, ListOfConfigurableSubclassFactoryAttributes):
                config[var_name] = []
                for sub_o in enumerate(getattr(o, var_name)):
                    config[var_name].append(cls.configurable_values_from_object(sub_o))
            elif isinstance(var, UsedConfig):
                continue
            else:
                raise ValueError(f"Unknown type {type(var)}")

        return config

    def save(self, file_path: Union[str, TextIO], comments: bool = True) -> None:
        """
        Saves configuration into file.

        :param file_path: path to file
        :param comments: true inserts comments
        """
        with open(file_path, "w") if isinstance(file_path, str) else nullcontext() as f:
            if not isinstance(file_path, str):
                f = file_path
            yaml = self.generate_yaml_config(comments=comments)
            YAML().dump(yaml, f)

    def _parse_file_override_user_defaults(self, attribute: ConfigurableAttribute) -> Optional[Dict]:
        """
        Parses file_override_user_defaults for given attribute that itself defines file_override_user_defaults,
        it is updated with the one used by this configuration.

        :param attribute: attribute to parse the file override user defaults for
        :return: parsed file_override_user_defaults
        :raise: ValueError when attribute not defines file_override_user_defaults
        """

        if not hasattr(attribute, "file_override_user_defaults"):
            raise ValueError(f"Attribute {attribute.__class__} doesn't define file_override_user_defaults")

        res = copy.deepcopy(attribute.file_override_user_defaults)
        if self.file_override_user_defaults is None or attribute.name not in self.file_override_user_defaults:
            return res

        for_update = self.file_override_user_defaults[attribute.name]
        if isinstance(attribute, ConfigurableSubclassFactory):
            for_update = for_update["config"]

        if res is None:
            return for_update

        res.update(for_update)

        return res

    def load(self, path_to: Optional[str] = None, use_program_arguments: bool = True) -> LoadedConfig[str, Any]:
        """
        Loads configuration from file and arguments.

        :param path_to: Path to YAML file with configuration.
         if None, then it is loaded from default path

         if default path is None, then it tries to load confiuration from default values
        :param use_program_arguments: true uses program arguments
        :return: loaded configuration
        """
        path_to = path_to if path_to is not None else self.path_to

        if path_to is None:
            return self.load_itself()
        
        with open(path_to, "r") as f:
            conf_dict = YAML().load(f)
            if use_program_arguments:
                conf_dict.update(self.get_values_from_arguments())
            return self.trans_and_val(conf_dict, path_to)

    def load_itself(self) -> LoadedConfig[str, Any]:
        """
        Loads configuration from default.

        :return: loaded configuration
        """
        conf_dict = self.generate_yaml_config()
        conf_dict.update(self.get_values_from_arguments())
        return self.trans_and_val(conf_dict, None)

    @staticmethod
    def bool_arg_convertor(value: str) -> bool:
        """
        Converts string to bool.

        :param value: string to convert
        :return: bool value
        """

        if value.lower() in ["true", "t", "1", "yes", "y"]:
            return True
        elif value.lower() in ["false", "f", "0", "no", "n"]:
            return False
        else:
            raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")

    def create_arg_parser(self) -> argparse.ArgumentParser:
        """
        It will create argument parser from value attributes on top level.

        :return: argument parser
        """
        parser = argparse.ArgumentParser(allow_abbrev=False)
        for var_name, var in get_configurable_attributes(self.cls_type).items():
            if ConfigurableFactory.should_omit(var_name, self.omit):
                continue

            if isinstance(var, ConfigurableValue):
                call_with = {
                    "help": var.desc,
                }

                if var.type is list:
                    if hasattr(var.type, "__args__") and len(var.type.__args__) == 1:
                        call_with["type"] = var.type.__args__[0]

                    call_with["nargs"] = "+"
                elif var.type in [str, int, float, bool]:
                    if var.type == bool:
                        call_with["type"] = self.bool_arg_convertor
                    else:
                        call_with["type"] = var.type
                else:
                    # it is expected that type will be transformed
                    call_with["type"] = str

                parser.add_argument("--" + var_name, **call_with)

        return parser

    def get_values_from_arguments(self) -> Dict[str, str]:
        """
        Gets key values from arguments.

        :return: values from arguments
        """
        args, _ = self.arg_parser.parse_known_args()
        return {k: v for k, v in vars(args).items() if v is not None}

    def trans_and_val_configurable_factory(self, attribute_name: str, attribute: ConfigurableFactory,
                                           value: Any, path_to: Optional[str]) -> Optional[LoadedConfig[str, Any]]:
        """
        Transforms and validates values in configuration for configurable factory attribute.

        :param attribute_name: name of attribute
        :param attribute: the configurable factory attribute
        :param value: loaded configuration value
        :param path_to: path to configuration file
        :return: transformed and validated configuration
        :raise: ConfigError when there is a problem with the value
        """
        try:
            if value is not None:  # not voluntary or not missing
                return Config(attribute.cls_type,
                              omit=self.pass_omit(self.omit, attribute_name, attribute),
                              allow_extra=self.allow_extra
                              ).trans_and_val(value, path_to)
        except ConfigError as e:
            raise ConfigError(e.msg, [attribute.name] + e.attribute)

    def trans_and_val_configurable_subclass_factory(self, attribute_name: str, attribute: ConfigurableSubclassFactory,
                                                    value: Any, path_to: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Transforms and validates values in configuration for configurable subclass factory attribute.

        :param attribute_name: name of attribute
        :param attribute: the configurable factory attribute
        :param value: loaded configuration value
        :param path_to: path to configuration file
        :return: transformed and validated configuration
        :raise: ConfigError when there is a problem with the value
        """
        try:
            if value is not None:  # not voluntary or not missing
                try:
                    c_name = value["cls"]
                except KeyError:
                    raise ConfigError("Missing attribute:", ["cls"])

                try:
                    c = sub_cls_from_its_name(attribute.parent_cls_type, c_name)
                except ValueError:
                    raise ConfigError(f"Invalid subclass name {c_name} for {attribute.parent_cls_type.__name__}:",
                                      ["cls"])

                try:
                    conf = value["config"]
                except KeyError:
                    raise ConfigError("Missing attribute:", ["config"])

                return {
                    "cls": c_name,
                    "config": Config(c,
                                     omit=self.pass_omit(self.omit, attribute_name, attribute),
                                     allow_extra=self.allow_extra).trans_and_val(conf, path_to)
                }

        except ConfigError as e:
            raise ConfigError(e.msg, [attribute.name] + e.attribute)

    def trans_and_val_configurable_value(self, attribute: ConfigurableValue, value: Any,
                                         path_to: Optional[str]) -> Optional[Any]:
        """
        Transforms and validates values in configuration for configurable value attribute.

        :param attribute: the configurable factory attribute
        :param value: loaded configuration value
        :param path_to: path to configuration file
        :return: transformed and validated configuration
        :raise: ConfigError when there is a problem with the value
        """
        if attribute.transform is not None:
            # firstly check whether the transform needs configuration path
            set_p = isinstance(attribute.transform, RelativePathTransformer) and attribute.transform.base_path is None
            if set_p:
                attribute.transform.base_path = str(Path(path_to).parent)

            try:
                value = attribute.transform(value)
            except Exception as e:
                raise ConfigError(f"Invalid value {value} ({e})", [attribute.name])

            if set_p:
                attribute.transform.base_path = None

        if attribute.validator is not None:
            try:
                res = attribute.validator(value)
            except Exception as e:
                raise ConfigError(f"Invalid value {value} ({e})", [attribute.name])

            if not res:
                raise ConfigError(f"Invalid value {value}", [attribute.name])

        return value

    def trans_and_val_list_of_configurable_subclass_factory(self, attribute_name: str,
                                                            attribute: ListOfConfigurableSubclassFactoryAttributes,
                                                            value: Any, path_to: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Transforms and validates values in configuration for list of configurable subclass factory attribute.

        :param attribute_name: name of attribute
        :param attribute: the configurable factory attribute
        :param value: loaded configuration value
        :param path_to: path to configuration file
        :return: transformed and validated configuration
        :raise: ConfigError when there is a problem with the value
        """

        if value is not None:  # not voluntary or not missing
            cur_res = []
            for i, c in enumerate(value):
                try:
                    cur_res.append(self.trans_and_val_configurable_subclass_factory(attribute_name,
                                                                                    attribute.configurable_subclass_factory,
                                                                                    c,
                                                                                    path_to))
                except ConfigError as e:
                    raise ConfigError(e.msg, [attribute.name, i] + e.attribute)
            return cur_res

    def trans_and_val(self, config: Dict[str, Any], path_to: Optional[str]) -> LoadedConfig[str, Any]:
        """
        Transforms and validates values in configuration.

        :param config: config for transformation and validation
        :param path_to: Path to file with configuration.
            is used by some transformation
        :return: Transformed and validated configuration
        """

        res_config = LoadedConfig()
        res_config.untransformed = config

        configurable_attributes = get_configurable_attributes(self.cls_type)
        # check for extra attributes
        if not self.allow_extra:
            in_config_names = set(k.name for k in configurable_attributes.values())
            for k in config.keys():
                if k not in in_config_names:
                    raise ConfigError(f"Extra attribute:", [k])

        for var_name, var in configurable_attributes.items():
            if var.hidden or ConfigurableFactory.should_omit(var_name, self.omit):
                continue

            try:
                v = config[var.name]
            except (TypeError, KeyError):
                if not var.voluntary:
                    raise ConfigError("Missing attribute:", [var.name])
                v = None
                if hasattr(var, "user_default"):
                    v = var.user_default
                    res_config.untransformed[var.name] = v
                elif var.type == Optional:
                    res_config.untransformed[var.name] = None

            res_config[var_name] = None

            if var.type is None and v is None:
                continue

            if isinstance(var, ConfigurableFactory):
                res_config[var_name] = self.trans_and_val_configurable_factory(var_name, var, v, path_to)
            elif isinstance(var, ConfigurableSubclassFactory):
                res_config[var_name] = self.trans_and_val_configurable_subclass_factory(var_name, var, v, path_to)
            elif isinstance(var, ListOfConfigurableSubclassFactoryAttributes):
                res_config[var_name] = self.trans_and_val_list_of_configurable_subclass_factory(var_name, var, v,
                                                                                                path_to)
            elif isinstance(var, ConfigurableValue):
                res_config[var_name] = self.trans_and_val_configurable_value(var, v, path_to)
            elif isinstance(var, UsedConfig):
                continue
            else:
                raise ConfigError("Unknown attribute type", [var_name])

        # add parent configurations

        for c in res_config.values():
            if isinstance(c, LoadedConfig):
                c.parent = res_config
        return res_config


class ConfigurableMixin:
    """
    Mixin that performs initialization of all configurables and calls __post_init__ after (if it exists).
    The validation is not performed here.
    """

    def __init__(self, **kargs):
        """
        Performs initialization of configurables.

        :param kargs: arguments for initialization
            if some argument is missing the default is used
        :raise KeyError: if some argument is missing and has no default value
        """
        self.__init_for_cls__(self.__class__, **kargs)

    def __init_for_cls__(self, cls, **kwargs):
        """
        Performs initialization of configurables, for defines object class.
        How this can be useful? For example, when you want to create a class that inherits from ConfigurableMixin,
        and you want to make sure that the mixin is only used for initializing the class, and not for initializing
        its subclasses.

        :param cls: class of object
        :param kwargs: arguments for initialization
        """

        for var_name, value in get_configurable_attributes(cls).items():
            if isinstance(value, ConfigurableAttribute):
                if var_name in kwargs:
                    setattr(self, var_name, kwargs[var_name])
                elif hasattr(value, "user_default"):
                    v = value.user_default
                    if hasattr(value, "transform") and value.transform is not None:
                        v = value.transform(v)
                    setattr(self, var_name, v)
                else:
                    raise KeyError(f"Missing attribute {var_name} for {cls.__name__}")

        if hasattr(cls, "__post_init__") and callable(getattr(cls, "__post_init__")):
            s = signature(self.__post_init__)
            params = {}
            for p in s.parameters.keys():
                params[p] = kwargs[p]
            self.__post_init__(**params)
