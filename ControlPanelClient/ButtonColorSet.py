from FhaCommon import Color, ControlPanelState


class ButtonColorSet:
    def __init__(self, colors_on, colors_dim, colors_minimal, colors_main=None):
        if (colors_main is None):
            colors_main = colors_on

        self.colors_on = colors_on
        self.colors_dim = colors_dim
        self.colors_minimal = colors_minimal
        self.colors_main = colors_main

    def get_color_for_control_panel_state(self, control_panel_state):
        if control_panel_state == ControlPanelState.PRE_INIT:
            return [Color.DARK_YELLOW, Color.DARK_YELLOW, Color.DARK_YELLOW]
        elif control_panel_state == ControlPanelState.ON:
            return self.get_color_for_on()
        elif control_panel_state == ControlPanelState.DIM:
            return self.get_color_for_dim()
        elif control_panel_state == ControlPanelState.MINIMAL:
            return self.get_color_for_minimal()
        elif control_panel_state == ControlPanelState.DARKENED:
            return self.get_color_for_darkened()
        elif control_panel_state == ControlPanelState.OFF:
            return self.get_color_for_off()
        elif control_panel_state == ControlPanelState.MAIN:
            return self.get_color_for_main()
        else:
            raise Exception("Could not find color for state: + " + str(control_panel_state))

    def get_color_for_on(self):
        return self.colors_on

    def get_color_for_dim(self):
        return self.colors_dim

    def get_color_for_minimal(self):
        return self.colors_minimal

    def get_color_for_darkened(self):
        return self.get_color_for_off()

    def get_color_for_off(self):
        return [Color.BLACK, Color.BLACK, Color.BLACK]

    def get_color_for_main(self):
        return self.colors_main


PRIMARY_BUTTON_COLOR_SET = ButtonColorSet(
    [Color.DIM_WHITE.as_rgb_array(), Color.WHITE_NEUTRAL.as_rgb_array(), Color.BLUE.as_rgb_array()],
    [Color.DARK_WHITE.as_rgb_array(), Color.DIM_WHITE.as_rgb_array(), Color.DIM_BLUE.as_rgb_array()],
    [Color.DARK_RED.as_rgb_array(), Color.DIM_RED.as_rgb_array(), Color.DIM_BLUE.as_rgb_array()],
    [Color.DIM_RED.as_rgb_array(), Color.RED.as_rgb_array(), Color.BLUE.as_rgb_array()]
)

SECONDARY_BUTTON_COLOR_SET = ButtonColorSet(
    [Color.DIM_BLUE.as_rgb_array(), Color.BLUE.as_rgb_array(), Color.RED.as_rgb_array()],
    [Color.DARK_BLUE.as_rgb_array(), Color.DIM_BLUE.as_rgb_array(), Color.DIM_RED.as_rgb_array()],
    [Color.BLACK.as_rgb_array(), Color.DIM_BLUE.as_rgb_array(), Color.DIM_RED.as_rgb_array()]
)

SPECIAL_BUTTON_COLOR_SET = ButtonColorSet(
    [Color.DIM_GREEN.as_rgb_array(), Color.GREEN.as_rgb_array(), Color.RED.as_rgb_array()],
    [Color.DARK_GREEN.as_rgb_array(), Color.DIM_GREEN.as_rgb_array(), Color.DIM_RED.as_rgb_array()],
    [Color.BLACK.as_rgb_array(), Color.DIM_GREEN.as_rgb_array(), Color.DIM_RED.as_rgb_array()]
)