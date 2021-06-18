from FhaDataObjects.NamedDataObject import NamedDataObject


class PanelState(NamedDataObject):
    def __init__(self, state):
        super().__init__('Panel State')
        self.state = state
