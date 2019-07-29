import datetime
import logging
import os
import webapp2

import models

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)


###############################################################################
class MainHandler(webapp2.RequestHandler):
    def get(self):
        params = {}
        q = models.UpdatedThing.query().order(-models.UpdatedThing.last_update)

        my_thing = None

        count = 0
        for thing in q.fetch():
            if my_thing is None:
                my_thing = thing
            count += 1

        params = {
            'count': count
        }
        if my_thing:
            params['update'] = my_thing.last_update

        render_template(self, 'index.html', params)


###############################################################################
mappings = [
    ('/', MainHandler),
]
app = webapp2.WSGIApplication(mappings, debug=True)
