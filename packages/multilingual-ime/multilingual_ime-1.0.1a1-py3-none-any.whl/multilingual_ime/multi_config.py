from typing import Optional
from .ime import (
    BOPOMOFO_IME,
    CANGJIE_IME,
    ENGLISH_IME,
    PINYIN_IME,
    JAPANESE_IME,
)

DEFAULT_CONFIG = {
    "selection_page_size": 5,
    "auto_phrase_learn": False,
    "auto_frequency_learn": False,
    "ime_activation_status": {
        BOPOMOFO_IME: True,
        CANGJIE_IME: True,
        ENGLISH_IME: True,
        PINYIN_IME: True,
        JAPANESE_IME: True,
    },
}


class MultiConfig:
    """
    MultiConfig is a class that manages the configuration settings for Multilingual IME.
    """

    def __init__(self, config_dict: Optional[dict] = None) -> None:
        if config_dict:
            self._config = config_dict
        else:
            self._config = DEFAULT_CONFIG

    @property
    def selection_page_size(self) -> int:
        """
        Get the selection page size.
        """
        return self._config["selection_page_size"]

    @property
    def auto_phase_learn_enabled(self) -> bool:
        """
        Get the auto phrase learn setting.
        """
        return self._config["auto_phrase_learn"]

    @property
    def auto_frequency_learn_enabled(self) -> bool:
        """
        Get the auto frequency learn setting.
        """
        return self._config["auto_frequency_learn"]

    @property
    def active_ime(self) -> list:
        """
        Get the list of active IMEs.
        """
        return [
            ime_name
            for ime_name, status in self._config["ime_activation_status"].items()
            if status
        ]

    def set_ime_activation_status(self, ime_name: str, status: bool) -> None:
        """
        Set the activation status of an IME.

        Args:
            ime_name (str): The name of the IME to activate or deactivate.
            status (bool): The activation status to set.
        """

        if ime_name not in self._config["ime_activation_status"]:
            raise ValueError(f"IME {ime_name} not found in config")

        if not isinstance(status, bool):
            raise ValueError(f"The status should be a boolean value got {type(status)}")

        self._config["ime_activation_status"][ime_name] = status

    def get_ime_activation_status(self, ime_name: str) -> bool:
        """
        Get the activation status of an IME.

        Args:
            ime_name (str): The name of the IME to get the status for.

        Returns:
            bool: The activation status of the IME.
        """
        if ime_name not in self._config["ime_activation_status"]:
            raise ValueError(f"IME {ime_name} not found in config")

        return self._config["ime_activation_status"][ime_name]

    def load_config(self, config_dict: dict) -> None:
        """
        Load configuration from a dictionary.
        If the dictionary is empty or invalid, raise a ValueError.
        """

        if not isinstance(config_dict, dict):
            raise ValueError(f"Config should be a dictionary, got {type(config_dict)}")
        if not config_dict:
            raise ValueError("Config dictionary is empty")

        for config_key, config_value in config_dict.items():
            if config_key not in DEFAULT_CONFIG:
                raise ValueError(f"Unknown config key: {config_key}")
            if not isinstance(config_value, type(DEFAULT_CONFIG[config_key])):
                raise ValueError(
                    f"Invalid type for config key {config_key}: "
                    f"expected {type(DEFAULT_CONFIG[config_key])}, got {type(config_value)}"
                )
            if config_key == "ime_activation_status":
                for activated_ime in config_value.keys():
                    if activated_ime not in DEFAULT_CONFIG["ime_activation_status"]:
                        raise ValueError(
                            f"Unknown IME in activation status: {activated_ime}"
                        )
                    if not isinstance(config_value[activated_ime], bool):
                        raise ValueError(
                            f"Invalid type for IME {activated_ime}: "
                            f"expected bool, got {type(config_value[activated_ime])}"
                        )

        for key in DEFAULT_CONFIG:
            if key not in config_dict:
                raise ValueError(f"Missing config key: {key}")
        self._config = config_dict

    def get_config(self) -> dict:
        """
        Get the current configuration as a dictionary.
        """
        return self._config
