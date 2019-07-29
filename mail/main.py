import datetime
import logging
import os
import webapp2

from google.appengine.api import mail
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
        render_template(self, 'index.html')


###############################################################################
class FormHandler(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name')
        message = self.request.get('message')
        email = self.request.get('email')

        params = {
          'name': name,
          'message': message,
          'email': email
        }

        # this has to be either an admin address, or:
        # YOUR_APP_ID@mail.appspot.mail.com - YOUR_APP_ID is your project ID
        from_address = 'contact@cs1520mail.appspotmail.com'
        subject = 'Contact from ' + name
        body = 'Message from ' + email + ':\n\n' + message
        mail.send_mail(from_address, 'timothyrjames@gmail.com', subject, body)

        render_template(self, 'contact.html', params)


###############################################################################
mappings = [
    ('/', MainHandler),
    ('/send-contact', FormHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)
