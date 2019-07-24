import datetime
import os
import webapp2

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.webapp import template


# We use this to reference our messages in memcache; we could just hardcode
# the 'messages' literal, but this makes sure we're consistent.
MESSAGES_KEY = 'messages'


# Retrieve messages, if the value exists; otherwise return an empty list.
def get_messages():
    messages = memcache.get(MESSAGES_KEY)
    if messages:
        return messages
    else:
        return []


# Retrieve the user email address, if the user is logged in; otherwise, None.
def get_user_email():
    user = users.get_current_user()
    if user:
        return user.email()
    else:
        return None


# Render a template for the given webapp2.RequestHandler.
def render_template(handler, file_name, template_values):

    template_file = 'templates/' + file_name

    # path to *this* python file.
    path_to_current_file = os.path.dirname(__file__)

    # path to the template file, assuming it's in the "templates" folder.
    path_to_template_file = os.path.join(path_to_current_file, template_file)

    # render the template with the given parameters.
    rendered_html = template.render(path_to_template_file, template_values)

    # write this out to the response for the handler.
    handler.response.out.write(rendered_html)


# A class to represent a simple chat message.
class Message():
    def __init__(self, user, timestamp, text):
        self.timestamp = timestamp
        self.text = text
        self.user = user


# Retrieve and display chat messages using the chat.html template.
class ChatHandler(webapp2.RequestHandler):
    def get(self):
        values = {
          'messages': get_messages()
        }
        render_template(self, 'chat.html', values)


# If the user is logged in, redirect to mainpage.html.
# If there is no user, redirect to the login url.
class MainPage(webapp2.RequestHandler):
    def get(self):
        if get_user_email():
            self.redirect('/i/mainpage.html')
        else:
            self.redirect(users.create_login_url('/'))


# Accept and process a chat message.
class SendHandler(webapp2.RequestHandler):
    def post(self):
        chat_message = self.request.get('chatmsg')
        if len(chat_message) > 4000:
            self.response.out.write("That message is too long.")
        else:
            timestamp = datetime.datetime.now()
            messages = get_messages()
            msg = Message(get_user_email(), timestamp, chat_message)
            messages.append(msg)
            # The following code ensures we don't have an overrun of messages.
            while len(messages) > 50:
                messages.pop(0)
            memcache.set(MESSAGES_KEY, messages)
            self.redirect("/")


# Identify our mappings from URLs to webapp2.RequestHandler objects.
app = webapp2.WSGIApplication([
  ('/chat', ChatHandler),
  ('/send', SendHandler),
  ('/.*', MainPage),
])
