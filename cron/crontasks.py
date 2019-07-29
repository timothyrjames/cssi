import time
import webapp2

import models

from google.appengine.api import mail
from google.appengine.ext import ndb

###############################################################################
class MinuteTaskHandler(webapp2.RequestHandler):
    def get(self):
        thing = models.UpdatedThing()
        thing.last_update = time.ctime()
        thing.put()


###############################################################################
class WedMailHandler(webapp2.RequestHandler):
    def get(self):
        mail.send_mail('contact@cs1520cron.appspotmail.com', 'someone@somewhere.com', 'hi!', 'here it is')


###############################################################################
mappings = [
    ('/tasks/minutetask', MinuteTaskHandler),
    ('/tasks/wedmail', WedMailHandler),
]
app = webapp2.WSGIApplication(mappings, debug=True)
