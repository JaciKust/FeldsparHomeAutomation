import datetime

import FhaCommon.Color as ColorConstant
import FhaServer.Interactable.Light.Light as LightConstant
from FhaCommon import ControlPanelState
from FhaServer.State.State import State


class AsleepLightsOffState(State):
    id = 1
    name = 'Asleep Lights Off'

    def __init__(self, wake_time, previous_state=None, auto_alarm=True):
        if auto_alarm:
            super().__init__(previous_state)
        else:
            super().__init__(previous_state)
        self.auto_alarm = auto_alarm
        self.wake_time = wake_time
        self.panel_state = ControlPanelState.MINIMAL

    def execute_state_change(self):
        super().execute_state_change()
        from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState

        transition_time = 0
        # If coming from Awake Lights On change over ten seconds
        if isinstance(self.previous_state, AwakeLightsOnState):
            transition_time = 10_000

        LightConstant.all_lamp.turn_off(transition_time)

        self.execute_default_accessories()

    # region Button Color

    def execute_default_accessories(self):
        pass
        # self.plant_lights.set_off()
        # self.fan.set_on()
        # self.oddish_light.set_off()
        # self.monitor.set_off()

    # endregion

    # region Button Actions

    def on_primary_short_press(self):
        from FhaServer.State.AsleepLightsOnState import AsleepLightsOnState
        return AsleepLightsOnState(self.wake_time, self, self.auto_alarm)

    def on_primary_long_press(self):
        from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState
        return AwakeLightsOnState(self)

    def on_primary_extra_long_press(self):
        return AsleepLightsOffState(self.wake_time, self.previous_state, not self.auto_alarm)

    # endregion

    # region On Event
    def on_time_check(self):
        # pass
        # super().on_time_check()
        #
        # current_time = datetime.datetime.now()
        #
        # # Should start the wake up process
        # if self.auto_alarm and self.wake_time < current_time:
        #     from FhaServer.State.WakingUpState1 import WakingUpState1
        #     return WakingUpState1(self.wake_time)
        return None

    # endregion

    def __str__(self):
        return super().__str__() + " Alarm set: " + str(self.auto_alarm)
