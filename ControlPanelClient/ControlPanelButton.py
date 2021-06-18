from events import Events

from FhaCommon import ControlPanelState
from FhaClient.RgbButton import RgbButton


class ControlPanelButton(RgbButton):
    def __init__(self, button_color_set, json_button):
        super().__init__(
            json_button.red_pwm_channel,
            json_button.green_pwm_channel,
            json_button.blue_pwm_channel,
            json_button.trigger_pin
        )

        self.name = json_button.name
        self.group = json_button.group
        self.category = json_button.category

        self.button_color_set = button_color_set
        self.state = ControlPanelState.PRE_INIT

        self.smart_button_events = Events()
        self.button_events.on_depressed += self._raise_smart_button_on_click

    def __del__(self):
        try:
            self.button_events.on_depressed -= self._raise_smart_button_on_click
        except:
            pass

    def _raise_smart_button_on_click(self, trigger_pin, button_press_time):
        # assert trigger_pin == self.trigger_pin, \
        #     "Why is this object handling a press event for a button with a different trigger_pin %s != %s"%\
        #     (trigger_pin, self.trigger_pin)
        self.smart_button_events.on_click(self.name, self.group, self.category, trigger_pin, button_press_time)

    def set_state(self, state):
        self.colors = self.button_color_set.get_color_for_control_panel_state(state)
        self.refresh_color()
