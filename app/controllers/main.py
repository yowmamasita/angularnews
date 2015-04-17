from ferris import Controller, route_with


class Main(Controller):

    @route_with('/')
    def list(self):
        pass
