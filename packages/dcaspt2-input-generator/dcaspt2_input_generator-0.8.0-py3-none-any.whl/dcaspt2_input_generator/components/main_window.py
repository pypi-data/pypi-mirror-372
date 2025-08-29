import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QSettings, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget

from dcaspt2_input_generator.components.data import colors, table_data
from dcaspt2_input_generator.components.menu_bar import MenuBar
from dcaspt2_input_generator.components.table_summary import TableSummary
from dcaspt2_input_generator.components.table_widget import TableWidget
from dcaspt2_input_generator.controller.color_settings_controller import ColorSettingsController
from dcaspt2_input_generator.controller.multi_process_controller import MultiProcessController
from dcaspt2_input_generator.controller.save_default_settings_controller import SaveDefaultSettingsController
from dcaspt2_input_generator.controller.widget_controller import WidgetController
from dcaspt2_input_generator.utils.dir_info import dir_info
from dcaspt2_input_generator.utils.settings import settings
from dcaspt2_input_generator.utils.utils import create_ras_str, debug_print


# Layout for the main window
# File, Settings, About (menu bar)
# message, AnimatedToggle (button)
# TableWidget (table)
# InputLayout (layout): inactive, active, secondary
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_UI()
        # employ native setting events to save/load form size and position
        self.settings = QSettings("Hiroshima University", "DIRAC-CASPT2 Input Generator")
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))  # type: ignore
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))  # type: ignore

    def init_UI(self):
        # Add drag and drop functionality
        self.setAcceptDrops(True)

        # Set task runner
        self.process = QProcess()
        self.callback = None
        # Show the header bar
        self.menu_bar = MenuBar()
        self.menu_bar.open_action_dirac.triggered.connect(self.select_file_Dirac)
        self.menu_bar.open_action_dfcoef.triggered.connect(self.select_file_DFCOEF)
        self.menu_bar.save_action_input.triggered.connect(self.save_input)
        self.menu_bar.save_action_dfcoef.triggered.connect(self.save_sum_dirac_dfcoef)

        # Body
        self.table_widget = TableWidget()
        self.table_summary = TableSummary()
        # Add Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_input)

        # Create an instance of WidgetController
        self.widget_controller = WidgetController(self.table_summary, self.table_widget)
        self.color_settings_controller = ColorSettingsController(
            self.table_widget, self.menu_bar.color_settings_action.color_settings_dialog
        )

        self.multi_process_controller = MultiProcessController(self.menu_bar.multi_process_action, settings)

        self.save_default_settings_controller = SaveDefaultSettingsController(
            color=colors,
            user_input=self.table_summary.user_input,
            multi_process_input=settings.multi_process_input,
            save_default_settings_action=self.menu_bar.save_default_settings_action,
        )
        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.menu_bar)
        layout.addWidget(self.table_widget)
        layout.addWidget(self.table_summary)
        layout.addWidget(self.save_button)

        # Create a widget to hold the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeEvent(self, a0) -> None:
        # save settings when closing
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        return super().closeEvent(a0)

    def save_input(self):
        def add_nelec(cur_nelec: int, rem_electrons: int) -> int:
            if rem_electrons > 0:
                cur_nelec += min(rem_electrons, 2)
            return cur_nelec

        # Create info for standard IVO input
        # E1g,u or E1?
        is_gerade_ungerade = True if table_data.header_info.spinor_num_info.keys() == {"E1g", "E1u"} else False
        if is_gerade_ungerade:
            nocc = {"E1g": 0, "E1u": 0}
            nvcut = {"E1g": 0, "E1u": 0}
        else:
            nocc = {"E1": 0}
            nvcut = {"E1": 0}
        inact = 0
        act = 0
        sec = 0
        elec = 0
        idx_caspt2 = 0
        ras1_list = []
        ras2_list = []
        ras3_list = []
        rem_electrons = table_data.header_info.electron_number
        is_cas = True
        last_ras2_idx = -1
        for idx in range(self.table_widget.rowCount()):
            spinor_indices = [2 * idx_caspt2 + 1, 2 * idx_caspt2 + 2]  # 1 row = 2 spinors
            item = self.table_widget.item(idx, 0)
            color = item.background()
            sym_str = item.text()

            if color != colors.not_used.color:
                idx_caspt2 += 1
            if color == colors.inactive.color:
                debug_print(f"{idx}, inactive")
                inact += 2
            elif color == colors.ras1.color:
                debug_print(f"{idx}, ras1")
                act += 2
                ras1_list.extend(spinor_indices)
                elec = add_nelec(elec, rem_electrons)
                is_cas = False
            elif color == colors.active.color:
                debug_print(f"{idx}, active")
                act += 2
                ras2_list.extend(spinor_indices)
                elec = add_nelec(elec, rem_electrons)
                if last_ras2_idx not in (-1, idx - 1):
                    is_cas = False
                last_ras2_idx = idx
            elif color == colors.ras3.color:
                debug_print(f"{idx}, ras3")
                act += 2
                elec = add_nelec(elec, rem_electrons)
                ras3_list.extend(spinor_indices)
                is_cas = False
            elif color == colors.secondary.color:
                debug_print(f"{idx}, secondary")
                sec += 2
            # nocc, nvcut
            if rem_electrons > 0:
                nocc[sym_str] += 1
            elif color != colors.not_used.color:
                # Reset nvcut
                for k in nvcut.keys():
                    nvcut[k] = 0
            else:
                nvcut[sym_str] += 1
            rem_electrons -= 2
        totsym = self.table_summary.user_input.totsym_number.get_value()

        output = f".ninact\n{inact}\n"
        output += f".nact\n{act}\n"
        output += f".nelec\n{elec}\n"
        output += f".nsec\n{sec}\n"
        output += f".caspt2_ciroots\n{totsym} 1\n"  # CASCI/CASPT2 root is fixed to 1
        if is_gerade_ungerade:
            output += f".noccg\n{nocc['E1g']}\n.noccu\n{nocc['E1u']}\n"
            output += "" if sum(nvcut.values()) == 0 else f".nvcutg\n{nvcut['E1g']}\n.nvcutu\n{nvcut['E1u']}\n"
        else:
            output += f".nocc\n{nocc['E1']}\n"
            output += "" if sum(nvcut.values()) == 0 else f".nvcut\n{nvcut['E1']}\n"
        output += f".diracver\n{self.table_summary.user_input.dirac_ver_number.get_value()}\n"
        output += "# NOTE: If you want to use this input to stand-alone version of DIRAC_CASPT2,\n"
        output += "# you cannot specify IVO and CASCI or CASPT2 simultaneously.\n"
        output += "# Please comment out subprograms depend on the calculation you want to run.\n"
        output += ".subprograms\nIVO\nCASCI\nCASPT2\n"
        if table_data.header_info.moltra_scheme is not None:
            output += f".scheme\n{table_data.header_info.moltra_scheme}\n"  # Explicitly set MOLTRA scheme.

        if not is_cas:
            ras1_str = create_ras_str(sorted(ras1_list))
            ras2_str = create_ras_str(sorted(ras2_list))
            ras3_str = create_ras_str(sorted(ras3_list))
            output += (
                ""
                if len(ras1_list) == 0
                else ".ras1\n" + ras1_str + "\n" + self.table_summary.user_input.ras1_max_hole_number.text() + "\n"
            )
            output += "" if len(ras2_list) == 0 else ".ras2\n" + ras2_str + "\n"
            output += (
                ""
                if len(ras3_list) == 0
                else ".ras3\n" + ras3_str + "\n" + self.table_summary.user_input.ras3_max_electron_number.text() + "\n"
            )
        output += ".end\n"

        # open dialog to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save dirac_caspt2 input File", "", "")
        if file_path:
            with open(file_path, mode="w") as f:
                f.write(output)

    def display_critical_error_message_box(self, message: str):
        QMessageBox.critical(self, "Error", message, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)

    def init_process(self):
        self.process.finished.connect(self.command_finished_handler)

        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()

    def command_finished_handler(self):
        if self.callback is not None:
            self.callback()
            self.callback = None
        self.process.kill()

    def run_sum_dirac_dfcoef(self, file_path):
        def create_command(command: str) -> str:
            if sys.executable:
                return f"{sys.executable} -m {command}"
            return command

        def check_version():
            command = create_command("sum_dirac_dfcoef -v")
            p = subprocess.run(
                command.split(),
                check=True,
                stdout=subprocess.PIPE,
            )
            output = p.stdout.decode("utf-8")
            # v4.0.0 or later is required
            major_version = int(output.split(".")[0])
            if major_version < 4:
                msg = f"The version of sum_dirac_dfcoef is too old.\n\
sum_dirac_dfcoef version: {output}\n\
Please update sum_dirac_dfcoef to v4.0.0 or later with `pip install -U sum_dirac_dfcoef`"
                raise Exception(msg)

        def run_command():
            num_process = max(1, settings.multi_process_input.multi_process_num)
            command = create_command(
                f'sum_dirac_dfcoef -i "{file_path}" -d 3 -c -o "{dir_info.sum_dirac_dfcoef_path}" -j {num_process}'
            )
            self.process.startCommand(command)
            if self.process.exitCode() != 0:
                data_stderr = self.process.readAllStandardError().data()
                if isinstance(data_stderr, (bytes, bytearray)):
                    decoded_stderr = data_stderr.decode()
                else:
                    decoded_stderr = data_stderr.tobytes().decode()
                err_msg = f"An error has ocurred while running the sum_dirac_dfcoef program.\n\
Please check the output file. path: {file_path}\nExecuted command: {command}\n\
all stderr: {decoded_stderr}"
                raise subprocess.CalledProcessError(self.process.exitCode(), command, "", err_msg)

        self.init_process()
        check_version()
        run_command()

    def select_file_Dirac(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "SELECT A DIRAC OUTPUT FILE", "", "Output file (*.out)")
        if file_path:
            try:
                self.callback = lambda: self.table_widget.reload(dir_info.sum_dirac_dfcoef_path)
                self.run_sum_dirac_dfcoef(file_path)
            except subprocess.CalledProcessError as e:
                err_msg = f"It seems that the sum_dirac_dfcoef program has failed.\n\
Please check the output file. Is this DIRAC output file?\npath: {file_path}\n\n\ndetails: {e.stderr}"
                self.display_critical_error_message_box(err_msg)
            except Exception as e:
                err_msg = f"An unexpected error has ocurred.\n\
file_path: {file_path}\n\n\ndetails: {e}"
                self.display_critical_error_message_box(err_msg)

    def select_file_DFCOEF(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT A sum_dirac_dfcoef OUTPUT FILE", "", "Output file (*.out)"
        )
        if file_path:
            try:
                self.reload_table(Path(file_path))
            except Exception as e:
                err_msg = f"An unexpected error has ocurred.\n\
file_path: {file_path}\n\n\ndetails: {e}"
                self.display_critical_error_message_box(err_msg)

    def save_sum_dirac_dfcoef(self):
        if not dir_info.sum_dirac_dfcoef_path.exists():
            QMessageBox.critical(
                self,
                "Error",
                "The sum_dirac_dfcoef.out file does not exist.\n\
Please run the sum_dirac_dfcoef program first.",
            )
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, caption="Save sum_dirac_dfcoef.out file as different name", filter="Output file (*.out)"
        )
        if not file_path.endswith(".out"):
            file_path += ".out"
        if file_path:
            import shutil

            # Copy the sum_dirac_dfcoef.out file to the file_path
            shutil.copy(dir_info.sum_dirac_dfcoef_path, file_path)

    def reload_table(self, filepath: Path):
        self.table_widget.reload(filepath)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        # Get the file path
        filename = event.mimeData().text()[8:]
        filepath = Path(filename).expanduser().resolve()
        if not filepath.exists():
            QMessageBox.critical(
                self,
                "Error",
                "The file cannot be found.\n\
Please check your dropped file.",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Cancel,
            )
        try:
            self.table_widget.reload(filepath)
        except Exception:
            try:
                self.callback = lambda: self.table_widget.reload(dir_info.sum_dirac_dfcoef_path)
                self.run_sum_dirac_dfcoef(filepath)
            except Exception:
                QMessageBox.critical(
                    self,
                    "Error",
                    "We cannot load the file properly.\n\
Please check your dropped file.",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Cancel,
                )

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        # Ctrl + S
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            self.save_input()
        # Ctrl + Shift + S
        elif (
            event.modifiers() == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
            and event.key() == Qt.Key.Key_S
        ):
            self.save_sum_dirac_dfcoef()
        # Ctrl + O
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_O:
            self.select_file_Dirac()
        # Ctrl + Shift + O
        elif (
            event.modifiers() == Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
            and event.key() == Qt.Key.Key_O
        ):
            self.select_file_DFCOEF()
        # Ctrl + ,
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Comma:
            self.menu_bar.color_settings_action.openColorSettingsDialog()
