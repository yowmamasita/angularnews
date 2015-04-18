from ferris.core.caching import cache
import requests
import time
from boltons.strutils import asciify

ONE_WEEK = 604800
API_URL = "http://hn.algolia.com"
API_VERSION = "v1"
MINIMUM_KARMA = 50
HITS_PER_PAGE = 50


def get_stories(tags, timestamp=None):
    if not timestamp:
        timestamp = int(time.time())

    @cache(key='get-stories-%s' % '-'.join(sorted(tags)), ttl=600)
    def inner(tags):
        ret = {}
        while tags:
            tag = tags.pop()
            page = 0
            nbPages = 2
            while page < nbPages - 1:
                url = "%s/api/%s/search?tags=story" % (API_URL, API_VERSION,)
                url += "&query=%s&numericFilters=points>=%d,created_at_i<=%d,created_at_i>%d&page=%d&hitsPerPage=%d" % (tag, MINIMUM_KARMA, timestamp, timestamp - ONE_WEEK, page, HITS_PER_PAGE)
                resp = requests.get(url)
                results = resp.json()
                page = int(results['page'])  # current page
                nbPages = int(results['nbPages'])  # total pages
                ret.update({
                    res['url'].encode('ascii'): {
                        'title': asciify(res['title']).encode('ascii'),
                        'url': res['url'].encode('ascii'),
                        'score': int(res['points']),
                        'tag': tag,
                    } for res in results['hits']
                })
        return ret

    return inner(tags)
