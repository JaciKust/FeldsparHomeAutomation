import datetime

import FhaCommon.Color as ColorConstant
import FhaServer.Interactable.Light.Light as LightConstant
from FhaServer.Constants import Time as TimeConstant
from FhaServer.State.WakingUpState import WakingUpState


class WakingUpState2(WakingUpState):
    id = 9
    name = 'Waking Up 2'

    def __init__(self, wake_up_time):
        super().__init__(wake_up_time)
        self.state_complete_time = wake_up_time + datetime.timedelta(
            minutes=TimeConstant.waking_up_1_duration_minutes + TimeConstant.waking_up_2_duration_minutes)

    def execute_state_change(self):
        super().execute_state_change()

        transition_time = TimeConstant.waking_up_2_duration_minutes * 60 * 1_000
        LightConstant.entry_lamp.turn_on(self.current_white, transition_time)
        LightConstant.jaci_bedside_lamp.turn_on(self.current_white, transition_time)

        # self.plant_lights.set_off()
        # self.fan.set_on()
        # self.oddish_light.set_off()
        # self.monitor.set_off()

    # region Button Color

    # endregion

    # region On Event

    def on_time_check(self):
        super().on_time_check()

        current_time = datetime.datetime.now()
        if current_time > self.state_complete_time:
            from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState
            return AwakeLightsOnState(self)
        return None

    # endregion

    def __str__(self):
        return super().__str__() + "Wake Time: " + str(self.wake_up_time)
