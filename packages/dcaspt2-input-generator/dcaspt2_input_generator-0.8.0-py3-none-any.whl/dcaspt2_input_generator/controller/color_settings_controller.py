from dcaspt2_input_generator.components.color_settings import ColorSettingsDialog
from dcaspt2_input_generator.components.data import colors
from dcaspt2_input_generator.components.table_widget import TableWidget
from dcaspt2_input_generator.utils.utils import debug_print


class ColorSettingsController:
    # table_widget: TableWidget
    # dialog: ColorSettingsDialog
    def __init__(self, table_widget: TableWidget, dialog: ColorSettingsDialog):
        self.table_widget = table_widget
        self.dialog = dialog

        # Connect signals and slots
        self.dialog.color_settings_changed.connect(self.onColorSettingsDialogChanged)

    def onColorSettingsDialogChanged(self):
        debug_print("onColorSettingsDialogChanged")
        prev_color = colors.deep_copy()
        color_type_str = self.dialog.buttonGroup.checkedButton().text()
        colors.change_color_templates(color_type_str)
        if prev_color != colors:
            self.table_widget.update_color(prev_color)
