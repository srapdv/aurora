"""Important set-ups for loading the special configs"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

import pathlib
import yaml


class CustomizationConfigLoader:
    """Represents a YAML config loader"""

    base_path = pathlib.Path(__file__).absolute()
    config_path = f"{base_path.parents[1]}/aurora/config/customization.yaml"

    @classmethod
    def load_special_models(cls):
        with open(cls.config_path, "r",) as stream:
            customization_config = yaml.load(stream, Loader=yaml.FullLoader)

        return customization_config["special_models"]

    @classmethod
    def load_customize_to(cls):
        with open(cls.config_path, "r",) as stream:
            customization_config = yaml.load(stream, Loader=yaml.FullLoader)

        return customization_config["customize_to"]


if __name__ == "__main__":
    config = CustomizationConfigLoader.load_special_models()
    print(config)
