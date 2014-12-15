from ferris import Model, ndb


class Story(Model):
    link = ndb.StringProperty()
