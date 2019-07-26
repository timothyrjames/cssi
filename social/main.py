import os
import socialdata
import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp import template


# This function will render a template for the given RequestHandler.
def render_template(handler, file_name, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates/', file_name)
    handler.response.out.write(template.render(path, template_values))


# If a user is logged in, return their email address; otherwise, None.
def get_user_email():
    user = users.get_current_user()
    if user:
        return user.email()
    else:
        return None


# Construct a dictionary of login / logout URL.
def get_template_parameters():
    values = {}
    if get_user_email():
        values['logout_url'] = users.create_logout_url('/')
    else:
        values['login_url'] = users.create_login_url('/')
    return values


# This is the catch-all handler that will show our main content page.
class MainHandler(webapp2.RequestHandler):
    def get(self):
        values = get_template_parameters()
        email = get_user_email()
        if email:
            # Somebody is logged in; we should show them their profile link.
            profile = socialdata.get_user_profile(email)
            if profile:
                values['name'] = profile.name
        render_template(self, 'mainpage.html', values)


# This handler is used to show the edit screen for the profile.
class ProfileEditHandler(webapp2.RequestHandler):
    def get(self):
        values = get_template_parameters()
        email = get_user_email()
        if not email:
            # if no user is logged in, we can show them the main page with
            # an error message.
            values['error_text'] = 'Please login to edit your profile.'
            render_template(self, 'mainpage.html', values)
            self.redirect('/')
        else:
            profile = socialdata.get_user_profile(email)
            if profile:
                values['name'] = profile.name
                values['description'] = profile.description
            render_template(self, 'profile-edit.html', values)


class ProfileSaveHandler(webapp2.RequestHandler):
    def post(self):
        email = get_user_email()
        values = get_template_parameters()
        if not email:
            values['error_text'] = 'Please login to save a profile.'
            render_template(self, 'mainpage.html', values)
        else:
            # We use "error_text" to collect errors.
            error_text = ''
            name = self.request.get('name')
            description = self.request.get('description')

            if len(name) < 2:
                error_text += 'Name should be at least 2 characters.\n'
            if len(name) > 20:
                error_text += 'Name should be no more than 20 characters.\n'
            if len(name.split()) > 1:
                error_text += 'Name should not have whitespace.\n'
            if len(description) > 4000:
                error_text += 'Description should be less than 4000 '
                error_text += 'characters.\n'
            for word in description.split():
                if len(word) > 50:
                    error_text += 'Description has words that are too long.\n'
                    break

            values['name'] = name
            values['description'] = description

            if error_text:
                # if any errors have occurred, we'll just tell the user.
                values['errormsg'] = error_text
            else:
                # if no errors have occurred, we'll save the data and let
                # the user know.
                error_text = socialdata.save_profile(email, name, description)
                if error_text:
                    # We just checked error_text, but one last thing could
                    # happen: the "name" could already exist.
                    values['errormsg'] = error_text
                else:
                    values['successmsg'] = 'Everything worked out fine.'
            # After all of this, we want to render the original edit view so
            # further edits can happen.
            render_template(self, 'profile-edit.html', values)


class ProfileViewHandler(webapp2.RequestHandler):
    def get(self, profilename):
        profile = socialdata.get_profile_by_name(profilename)
        values = get_template_parameters()

        # Assume that there is no profile, and fill in values if it exists.
        values['name'] = 'Unknown'
        values['description'] = 'Profile does not exist.'
        if profile:
            # If we have a profile, then add those to our template values.
            values['name'] = profile.name
            values['description'] = profile.description
        render_template(self, 'profile-view.html', values)


class ProfileListHandler(webapp2.RequestHandler):
    def get(self):
        profiles = socialdata.get_recent_profiles()
        values = get_template_parameters()
        values['profiles'] = profiles
        render_template(self, 'profile-list.html', values)


app = webapp2.WSGIApplication([
    ('/p/(.*)', ProfileViewHandler),
    ('/profile-list', ProfileListHandler),
    ('/profile-save', ProfileSaveHandler),
    ('/profile-edit', ProfileEditHandler),
    ('.*', MainHandler),
])
