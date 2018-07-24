import json
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users


# This is a simple model that we can use to demo storage & retrieval.
class TestModel(ndb.Model):
  title = ndb.StringProperty()
  text = ndb.TextProperty()
  author = ndb.StringProperty()
  
  # we'll create a simple summary dictionary method here
  def to_summary_dict(self):
    return {
      # "key" is a property we get from ndb.Model - we can use this for easy retrieval of 1 specfic Model
      'key': self.key.urlsafe(),
      'title': self.title,
      'author': self.author
    }
    
  # this to_dict method will send *all* of the data for this object
  def to_dict(self):
    result = self.to_summary_dict()
    result['text'] = self.text
    return result


# convenience function for retrieving a user, or None if the user isn't logged in
def get_user_email():
  user = users.get_current_user()
  if user:
    return user.email()
  else:
    return None
    

# convenience function for sending JSON data to browser
def send_json(request_handler, params):
  # params should be a dictionary - we'll just write it out as a JSON object
  request_handler.response.out.write(json.dumps(params))
  
  
# convenience funtion for sending JSON error msg to browser
def send_error(request_handler, msg):
  # we will create a dictionary, and just convert that to a JSON response
  request_handler.response.out.write(json.dumps({'error': msg}))
  

# Handler for displaying user email JSON - URLs for login and logout
class UserHandler(webapp2.RequestHandler):
  def dispatch(self):
    result = {
      'login': users.create_login_url('/'),
      'logout': users.create_logout_url('/'),
      'user': get_user_email(),
    }
    send_json(self, result)
    

# this handler just lists our models in JSON
class ListModelsHandler(webapp2.RequestHandler):
  def dispatch(self):
    if get_user_email():
      # if we get this far, we know we have a valid user
      result = {}
      result['models'] = []
      
      # retrieve all of the models we have:
      for model in TestModel.query().fetch():
        result['models'].append(model.to_summary_dict())
        
      send_json(self, result)

    else:
      send_error(self, 'Please log in.')
      
      
# retrieve the parameters from the request, build a model, and store it
class AddModelHandler(webapp2.RequestHandler):
  def dispatch(self):
    if get_user_email():
      rtext = self.request.get('text')
      rtitle = self.request.get('title')
      if len(rtitle) > 500:
        send_error(self, 'Title should be less than 500 characters.')
      
      elif rtitle.strip():
        m = TestModel(title=rtitle, text=rtext, author=get_user_email())
        m.put()
        send_json(self, {'ok': True})
        
      else:
        send_error(self, 'Title should not be blank.')

    else:
      send_error(self, 'Please log in.')
      

# retrieve the detail for one model
class ModelDetailHandler(webapp2.RequestHandler):
  def dispatch(self):
    if get_user_email():
      # get the key from the request
      rkey = self.request.get('key')
      
      # construct an ndb.Key object
      key = ndb.Key(urlsafe=rkey)
      if key:
        # use the ndb.Key object's get() method to retrieve the Model associated with that particular key
        m = key.get()
        send_json(self, m.to_dict())
      else:
        send_error(self, 'Model not found.')
    else:
      send_error('Please log in.')


app = webapp2.WSGIApplication([
  ('/models', ListModelsHandler),
  ('/user', UserHandler),
  ('/add', AddModelHandler),
  ('/model', ModelDetailHandler),
])









