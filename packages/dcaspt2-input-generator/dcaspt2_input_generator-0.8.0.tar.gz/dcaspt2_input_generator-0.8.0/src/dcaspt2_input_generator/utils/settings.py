# This script contains all functions to handle settings of this application.

import json
import os
from pathlib import Path
from typing import Dict, Union

from dcaspt2_input_generator.utils.dir_info import dir_info


class CustomJsonDecodeError(json.decoder.JSONDecodeError):
    def __init__(self, settings_file_path: Path):
        self.message = f"settings.json is broken. Please delete the file and restart this application.\n\
File path: {settings_file_path}"
        super().__init__(self.message, self.doc, self.pos)


class SettingsDict(Dict[str, Union[str, int]]):
    pass


class UserInput:
    total_symmetry: int
    ras1_max_hole: int
    ras3_max_electron: int
    dirac_ver: int
    json_dict: SettingsDict

    def __init__(self, json_dict: SettingsDict, default_settings: SettingsDict) -> None:
        # If the settings.json file exists, read the settings from the file
        self.json_dict = json_dict
        keys = ["total_symmetry", "ras1_max_hole", "ras3_max_electron", "dirac_ver"]
        for key in keys:
            if key in self.json_dict:
                setattr(self, key, int(self.json_dict[key]))
            elif key in default_settings:
                setattr(self, key, int(default_settings[key]))
            else:
                print(f"skip key {key}")
                pass # key is not in settings file nor default settings, skip it


class ColorTheme:
    def __init__(self, json_dict: SettingsDict) -> None:
        self.json_dict = json_dict
        self.theme_list = ["default", "Color type 1", "Color type 2"]
        self.theme_name = self.get_color_theme_name()

    def get_color_theme_name(self) -> str:
        key = "color_theme"
        if key in self.json_dict and self.json_dict[key] in self.theme_list:
            return str(self.json_dict[key])
        return "default"


class MultiProcess:
    def __init__(self, json_dict: SettingsDict) -> None:
        self.json_dict = json_dict
        self.multi_process_num = self.__init_multi_process_num__()

    def __init_multi_process_num__(self) -> int:
        num_process = 4  # default
        key = "multi_process_num"
        if key in self.json_dict:
            num_process = int(self.json_dict[key])
        # If the number of CPU cores is less than the number of processes, use the number of CPU cores.
        cpu_count = os.cpu_count()
        num_process = num_process if cpu_count is None else min(cpu_count, num_process)
        return num_process


class Settings:
    def __init__(self):
        # Application Default Settings
        self.default_settings = SettingsDict(
            {
                "total_symmetry": 1,
                "ras1_max_hole": 0,
                "ras3_max_electron": 0,
                "dirac_ver": 23,
                "color_theme": "default",
                "multi_process_num": 4,
            }
        )
        if not dir_info.setting_file_path.exists():
            self.create_default_settings_file()
        try:
            self.json_dict: SettingsDict = json.load(open(dir_info.setting_file_path))
        except CustomJsonDecodeError as e:
            raise CustomJsonDecodeError(dir_info.setting_file_path) from e
        self.input = UserInput(self.json_dict, self.default_settings)
        self.color_theme = ColorTheme(self.json_dict)
        self.multi_process_input = MultiProcess(self.json_dict)

    def create_default_settings_file(self):
        with open(dir_info.setting_file_path, mode="w") as f:
            json.dump(self.default_settings, f, indent=4)


settings = Settings()
