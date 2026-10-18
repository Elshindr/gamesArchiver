from .commsview import CommsView

class CommsController:
    def __init__(self, page, engine):
        self.page = page
        self.engine = engine

    def set_page(self):
        return CommsView.get_tabs_comms()