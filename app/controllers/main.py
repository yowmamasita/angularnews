from ferris import Controller, messages, route_with
from app.models.story import Story
import requests
import time

THREE_MONTHS = 7889220
SIX_MONTHS = 15778440
API_URL = "http://hn.algolia.com"
API_VERSION = "v1"


class Main(Controller):
    class Meta:
        components = (messages.Messaging,)
        prefixes = ('api',)
        Model = Story

    @route_with('/')
    def api_list(self):
        timestamp = int(time.time())
        ret = []
        tags = ['angular', 'angularjs']
        for tag in tags:
            url = API_URL + "/api/" + API_VERSION + "/search?tags=story"
            url += "&query=%s&numericFilters=points>=50,created_at_i>=" % tag
            resp = requests.get(url + str(timestamp - THREE_MONTHS))
            results = resp.json()
            print results['page']
            print results['nbHits']
            print results['nbPages']
            print results['hitsPerPage']
            print '-----------------'
            for hit in results['hits']:
                ret.append(Story(**{k: v for k, v in hit.iteritems() if k in Story._properties.keys()}))
        self.context['data'] = ret
