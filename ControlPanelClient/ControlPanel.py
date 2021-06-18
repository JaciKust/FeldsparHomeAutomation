from events import Events

from FhaCommon import ControlPanelState


class ControlPanel:
    def __init__(self, buttons, name):
        self.buttons = buttons
        self.state = ControlPanelState.ON
        self.name = name
        self._set_up_buttons()

    def _set_up_buttons(self):
        for button in self.buttons:
            button.smart_button_events.on_click += self._on_button_click

    def set_control_panel_state(self, state):
        self.state = state
        self._set_button_state()

    def _set_button_state(self):
        for button in self.buttons:
            button.set_state(self.state)

    def force_button_update(self):
        for button in self.buttons:
            button.refresh_color()

    input_events = Events()

    def _on_button_click(self, name, group, category, trigger_pin, button_press_time):
        self.input_events.on_control_clicked(name, group, category, trigger_pin, button_press_time, self.name)
