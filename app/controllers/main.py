from ferris import Controller, route_with
from app.services.hackernews import get_stories


class Main(Controller):

    @route_with('/')
    def list(self):
        tags = ['python', 'javascript', 'angular', 'angularjs']
        self.context['links'] = get_stories(tags)

    @route_with('/<tags>')
    def search(self, tags):
        # self.meta.change_view('Template')
        self.meta.view.template_name = 'main/list.html'
        self.context['links'] = get_stories(tags.split('&'))
