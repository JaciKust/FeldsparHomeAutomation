from FhaDataObjects.NamedDataObject import NamedDataObject


class ButtonClickEvent(NamedDataObject):
    def __init__(self, button_name, group, category, trigger_pin, button_press_time):
        super().__init__('Button Click')
        self.button_name = button_name
        self.group = group
        self.category = category
        #TODO: Determine if this is needed (No)
        self.trigger_pin = trigger_pin
        self.button_press_time = button_press_time