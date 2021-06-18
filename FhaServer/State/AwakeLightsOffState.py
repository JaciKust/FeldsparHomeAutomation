import FhaCommon.Color as ColorConstant
import FhaServer.Interactable.Light.Light as LightConstant
from FhaCommon import ControlPanelState
from FhaServer import TimeFunctions
from FhaServer.Constants import Time as TimeConstant
from FhaServer.State.State import State

class AwakeLightsOffState(State):
    id = 3
    name = 'Awake Lights Off'
    ring_color = ColorConstant.DIM_WHITE
    on_press_ring_color = ColorConstant.DARK_WHITE
    on_long_press_ring_color = ColorConstant.BLUE

    def __init__(self, previous_state=None):
        super().__init__(previous_state)
        self.panel_state = ControlPanelState.DIM

    def execute_state_change(self):
        super().execute_state_change()
        LightConstant.all_lamp.turn_off(1000)

        # self.plant_lights.soft_set_on()
        # self.fan.set_off()
        # self.oddish_light.soft_set_on()
        # self.monitor.set_off()

    def on_time_check(self):
        super().on_time_check()
        pass
        # self.plant_lights.set_on_if_under_max_time()
        # self.oddish_light.set_on_if_under_max_time()

    # region Button Color

    # endregion

    # region Button Actions

    def on_primary_short_press(self):
        from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState
        return AwakeLightsOnState(self)

    def on_primary_long_press(self):
        from FhaServer.State.AsleepLightsOffState import AsleepLightsOffState
        return AsleepLightsOffState(TimeFunctions.get_next(TimeConstant.wakeup_time), self)

    def on_primary_extra_long_press(self):
        from FhaServer.State.Rainbow.RainbowState import RainbowState
        return RainbowState()

    def on_door_short_press(self):
        return self.on_primary_short_press()

    # endregion
