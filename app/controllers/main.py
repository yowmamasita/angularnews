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
        url = API_URL + "/api/" + API_VERSION + "/search?tags=story"
        url += "&query=angular&numericFilters=points>=50,created_at_i>="
        resp = requests.get(url + str(timestamp - THREE_MONTHS))
        results = resp.json()
        for hit in results['hits']:
            print hit['title'].encode('utf-8')
            print hit['url']
        return 'ok'
