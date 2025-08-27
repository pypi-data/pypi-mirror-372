# -*- coding: UTF-8 -*-
"""
Created on 10.11.22

:author:     Martin Dočekal
"""
import os
from pathlib import Path
from unittest import TestCase

from classconfig import Config, \
    ConfigurableMixin
from classconfig import ConfigurableValue, ConfigurableFactory


class Inventory(ConfigurableMixin):
    size: int = ConfigurableValue(desc="Size of an inventory", user_default=10, validator=lambda x: x > 0)


class Character(ConfigurableMixin):
    lvl: int = ConfigurableValue(desc="Level of a character", user_default=1, validator=lambda x: x > 0)
    name: str = ConfigurableValue(desc="Name of a character")
    inventory: Inventory = ConfigurableFactory(desc="Character's inventory", cls_type=Inventory)


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TMP_DIR = os.path.join(SCRIPT_DIR, "tmp")
FIXTURE_DIR = os.path.join(SCRIPT_DIR, "fixtures")
TMP_PATH_TO_CONFIG = str(Path(TMP_DIR) / "config.yaml")
FIXTURE_PATH_TO_CONFIG = str(Path(FIXTURE_DIR) / "readme_character.yaml")
FIXTURE_PATH_TO_FILLED_CONFIG = str(Path(FIXTURE_DIR) / "readme_character_filled.yaml")


class TestREADME(TestCase):

    def tearDown(self) -> None:
        try:
            os.remove(TMP_PATH_TO_CONFIG)
        except FileNotFoundError:
            pass

    def test_save_characters_config(self):
        """
        Test that is used in README.md
        """
        Config(Character).save(TMP_PATH_TO_CONFIG)

        with open(TMP_PATH_TO_CONFIG, "r") as f, open(FIXTURE_PATH_TO_CONFIG, "r") as f2:
            self.assertEqual(f2.read(), f.read())

    def test_load_characters_config(self):
        """
        Test that is used in README.md
        """
        config = Config(Character).load(FIXTURE_PATH_TO_FILLED_CONFIG)
        loaded_obj = ConfigurableFactory(Character).create(config)

        self.assertEqual(1, loaded_obj.lvl)
        self.assertEqual("Alan", loaded_obj.name)
        self.assertEqual(20, loaded_obj.inventory.size)
