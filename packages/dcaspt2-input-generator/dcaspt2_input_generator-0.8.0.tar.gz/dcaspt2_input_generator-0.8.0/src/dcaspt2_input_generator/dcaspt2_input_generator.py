import os
import sys

from PySide6.QtWidgets import QApplication

from dcaspt2_input_generator.utils.dir_info import dir_info

# import qt_material


class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.init_gui()

    def init_gui(self):
        from dcaspt2_input_generator.components.main_window import MainWindow

        self.window = MainWindow(parent=None)
        self.window.setWindowTitle("DIRAC-CASPT2 Input Generator")
        self.window.show()

    def delete_unneeded_files(self):
        if dir_info.sum_dirac_dfcoef_path.exists():
            os.remove(dir_info.sum_dirac_dfcoef_path)

    def run(self):
        try:
            sys.exit(self.app.exec_())
        except SystemExit:
            self.delete_unneeded_files()


def main():
    app = MainApp()
    app.run()
