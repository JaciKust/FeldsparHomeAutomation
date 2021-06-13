class ControlPanel:
    def __init__(self, buttons):
        self.buttons = buttons

    def set_button_colors(self, button_colors):
        for button in self.buttons:
            button.set_if_for(button_colors)

    def get_button_from_channel(self, channel):
        for button in self.buttons:
            if button.trigger_pin == channel:
                return button
        return None
