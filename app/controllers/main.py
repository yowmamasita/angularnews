from ferris import Controller, messages, route_with
from app.models.story import Story


class Main(Controller):
    class Meta:
        components = (messages.Messaging,)
        prefixes = ('api',)
        Model = Story

    @route_with('/')
    def api_list(self):
        return 200
