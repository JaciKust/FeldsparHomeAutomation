import datetime

from FhaCommon import ControlPanelState
from FhaServer.Constants import Time as TimeConstant
from FhaServer.State.State import State


class WakingUpState(State):

    def __init__(self, wake_up_time):
        self.wake_up_time = wake_up_time
        super().__init__(None)
        self.panel_state = ControlPanelState.MINIMAL

    # region Button Actions

    def on_primary_short_press(self):
        # Snooze
        new_wake_time = datetime.datetime.now() + datetime.timedelta(minutes=TimeConstant.snooze_time)
        from FhaServer.State.AsleepLightsOffState import AsleepLightsOffState
        return AsleepLightsOffState(new_wake_time, self)

    def on_primary_long_press(self):
        # Wake Up
        from FhaServer.State.AwakeLightsOnState import AwakeLightsOnState
        return AwakeLightsOnState(self)

    def on_primary_extra_long_press(self):
        # Turn off Alarm
        from FhaServer.State.AsleepLightsOffState import AsleepLightsOffState
        return AsleepLightsOffState(self.wake_up_time, self, False)

    # endregion
