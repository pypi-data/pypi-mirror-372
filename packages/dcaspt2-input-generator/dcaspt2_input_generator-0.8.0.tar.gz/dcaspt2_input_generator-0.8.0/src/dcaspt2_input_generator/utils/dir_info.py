from pathlib import Path


class DirInfo:
    def __init__(self):
        self.user_current_dir = Path.cwd()
        self.app_default_save_dir = Path.home() / ".dcaspt2_input_generator"
        self.app_rootdir = Path(__file__).parent.parent.expanduser().resolve()  # src/dcaspt2_input_generator
        self.setting_file_path = self.app_default_save_dir / "settings.json"
        self.sum_dirac_dfcoef_path = self.app_default_save_dir / "sum_dirac_dfcoef.out"
        self.ivo_input_path = self.app_default_save_dir / "active.ivo.inp"
        self.__init_mkdir()

    def __init_mkdir(self):
        self.app_default_save_dir.mkdir(parents=True, exist_ok=True)


dir_info = DirInfo()
