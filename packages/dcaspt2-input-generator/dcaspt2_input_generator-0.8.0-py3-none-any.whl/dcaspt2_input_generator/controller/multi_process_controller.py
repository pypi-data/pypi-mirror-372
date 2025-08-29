from dcaspt2_input_generator.components.menu_bar import MultiProcessDialogAction
from dcaspt2_input_generator.utils.settings import Settings


class MultiProcessController:
    def __init__(self, multi_process_action: MultiProcessDialogAction, settings: Settings):
        self.multi_process_action = multi_process_action
        self.settings = settings

        # Connect signals and slots
        self.multi_process_action.multi_process_settings.multi_process_changed.connect(self.onMultiProcessDialogChanged)

    def onMultiProcessDialogChanged(self):
        self.settings.multi_process_input.multi_process_num = (
            self.multi_process_action.multi_process_settings.multi_process_spin_box.value()
        )
