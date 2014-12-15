from ferris import Model, ndb


class Story(Model):
    title = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
