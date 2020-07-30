"""Important set-ups for loading the special configs"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

import pathlib
import yaml


class ConfigLoader:
    """Represents a YAML config loader"""

    @staticmethod
    def load_special_models():
        base_path = pathlib.Path(__file__).absolute()
        config_path = f"{base_path.parents[1]}/aurora/config/customization.yaml"

        print(config_path)

        with open(config_path, "r",) as stream:
            customization_config = yaml.load(stream, Loader=yaml.FullLoader)

        return customization_config


CUSTOMIZATION_CONFIG = ConfigLoader.load_special_models()

if __name__ == "__main__":
    config = ConfigLoader.load_special_models()
    print(config)
