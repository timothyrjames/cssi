from google.appengine.ext import ndb

class UpdatedThing(ndb.Model):
    last_update = ndb.StringProperty()
