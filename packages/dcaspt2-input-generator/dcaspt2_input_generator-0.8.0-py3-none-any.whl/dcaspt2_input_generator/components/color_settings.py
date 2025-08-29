from dcaspt2_input_generator.utils.settings import settings
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QButtonGroup, QDialog, QRadioButton, QVBoxLayout, QWidget


class ColorSettingsDialog(QDialog):
    color_settings_changed = Signal()

    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.buttonGroup = QButtonGroup(self)
        for idx, color in enumerate(settings.color_theme.theme_list):
            button = QRadioButton(color, self)
            if idx == 0:
                button.setChecked(True)
            self.buttonGroup.addButton(button)
            self.buttonGroup.setId(button, idx)
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonClicked.connect(self.button_clicked)

        # Add the radio buttons to the layout
        layout = QVBoxLayout()
        for btn in self.buttonGroup.buttons():
            layout.addWidget(btn)

        # Create a widget to hold the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Show the widget as a dialog
        self.setWindowTitle("Color Settings")
        self.setLayout(layout)

    # When buttonClicked is emitted, the signal is connected to the slot color_settings_changed
    def button_clicked(self):
        self.color_settings_changed.emit()


class ColorSettingsDialogAction(QAction):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.color_settings_dialog = ColorSettingsDialog()
        self.setText("Color Settings")
        self.triggered.connect(self.openColorSettingsDialog)

    def openColorSettingsDialog(self):
        self.color_settings_dialog.exec()
