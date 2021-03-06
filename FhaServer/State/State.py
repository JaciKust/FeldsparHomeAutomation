import logging
import threading
from datetime import datetime, timedelta

import FhaCommon.Color as ColorConstant
from FhaCommon import ControlPanelState
from FhaCommon.Constants import Button as ButtonConstant
from FhaDataAccess.MarraQueryMaker import MarraQueryMaker


class State:
    name = 'Base State'
    id = -1

    def __init__(self, previous_state):
        self.previous_state = previous_state

        #transmitter433 = Transmitter433()
        # self.fan = transmitter433.fan
        # self.monitor = transmitter433.monitors
        # self.plant_lights = transmitter433.plant_lights
        # self.oddish_light = RelayConstant.ODDISH_RELAY
        # self.sound_system_relay = RelayConstant.SOUND_SYSTEM_RELAY
        # self.power_relay = RelayConstant.POWER_RELAY

        self._last_run = datetime.now()

        self.maker = MarraQueryMaker.getInstance()
        if previous_state is None or previous_state.current_white is None:
            self.current_white = ColorConstant.WHITES_IN_KELVIN_CYCLE[ColorConstant.WHITE_START_INDEX]
        else:
            self.current_white = previous_state.current_white

    def execute_state_change(self):
        # print("State changed to " + self.name)
        thread = threading.Thread(target=self._update_database)
        thread.start()

    def execute_state_leave(self):
        pass

    def _update_database(self):
        try:
            self.maker.insert_state_status(self.id)
        except:
            print("Unable to update database state for " + str(self.id))
            pass

    # region Button Color

    panel_state = ControlPanelState.PRE_INIT

    # endregion

    # region Button Actions

    def on_primary_short_press(self):
        return None

    def on_primary_long_press(self):
        return None

    def on_primary_extra_long_press(self):
        return None

    def on_secondary_short_press(self):
        #self.fan.toggle()
        return None

    def on_secondary_long_press(self):
        # self.plant_lights.toggle()
        # if self.plant_lights.get_is_on():
        #     self.oddish_light.set_on()
        # else:
        #     self.oddish_light.set_off()
        return None

    def on_secondary_extra_long_press(self):
        # self.monitor.toggle()
        return None

    def on_door_short_press(self):
        return None

    def on_door_long_press(self):
        return None

    def on_door_extra_long_press(self):
        return None

    def on_desk_right_short_press(self):
        return self.on_secondary_short_press()

    def on_desk_right_long_press(self):
        return self.on_secondary_long_press()

    def on_desk_right_extra_long_press(self):
        return self.on_secondary_extra_long_press()

    def on_desk_left_short_press(self):
        return self.on_primary_short_press()

    def on_desk_left_long_press(self):
        return self.on_primary_long_press()

    def on_desk_left_extra_long_press(self):
        return self.on_primary_extra_long_press()

    def on_desk_rear_short_press(self):
        self.cycle_kelvin()

    def on_desk_rear_long_press(self):
        pass #self.power_relay.pulse_on_off()

    def on_desk_rear_extra_long_press(self):
        pass #self.sound_system_relay.toggle()

    # endregion

    # region Light Kelvin Change

    current_white = None

    def on_kelvin_changed(self):
        pass

    def cycle_kelvin(self):
        pass
        # try:
        #     location = ColorConstant.WHITES_IN_KELVIN_CYCLE.index(self.current_white)
        # except:
        #     location = -1
        # location += 1
        # location %= len(ColorConstant.WHITES_IN_KELVIN_CYCLE)
        # self.current_white = ColorConstant.WHITES_IN_KELVIN_CYCLE[location]
        # self.on_kelvin_changed()

    def set_default_white(self):
        pass

    # endregion

    # region Get State for Button

    def get_state_for(self, category, button_press_time):
        if category == 'Primary':
            return self.get_state_for_primary_button(button_press_time)
        elif category == 'Accessory':
            return self.get_state_for_secondary_button(button_press_time)
        elif category == 'Special':
            # TODO
            pass

    def get_state_for_primary_button(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_primary_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_primary_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_primary_short_press()
        return return_state

    def get_state_for_secondary_button(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_secondary_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_secondary_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_secondary_short_press()
        return return_state

    def get_state_for_door_button(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_door_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_door_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_door_short_press()
        return return_state

    def get_state_for_desk_right(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_desk_right_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_desk_right_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_desk_right_short_press()
        return return_state

    def get_state_for_desk_left(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_desk_left_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_desk_left_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_desk_left_short_press()
        return return_state

    def get_state_for_desk_rear(self, button_time):
        return_state = None

        # extra long press
        if button_time >= ButtonConstant.EXTRA_LONG_PRESS_MIN:
            return_state = self.on_desk_rear_extra_long_press()

        # long button press
        elif button_time >= ButtonConstant.LONG_PRESS_MIN:
            return_state = self.on_desk_rear_long_press()

        # short press
        elif button_time >= ButtonConstant.NOISE_THRESHOLD:
            return_state = self.on_desk_rear_short_press()

        return return_state

    # endregion

    # region Time

    def on_time_check(self):
        pass
        # self.plant_lights.set_off_if_over_max_time()
        # self.oddish_light.set_off_if_over_max_time()
        #
        # self._write_plants_to_db_if_necessary()

    def _write_plants_to_db_if_necessary(self):
        pass
        # current_time = datetime.now()
        #
        # if self._last_run is None:
        #     self._last_run = current_time
        #
        # # logic to be hit once a day shortly after 0:07
        # if (current_time.hour == 0 and 6 < current_time.minute < 9
        #     or current_time.hour == 23 and 46 < current_time.minute < 49) \
        #         and current_time - self._last_run > timedelta(minutes=5):
        #     self._last_run = current_time
        #
        #     self.oddish_light.write_current_state_to_database()
        #     self.plant_lights.write_current_state_to_database()
        #     print("\tRunning write.")

    # endregion

    def __eq__(self, other):
        return other.id == self.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name
