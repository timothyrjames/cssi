import datetime
import logging
import os
import webapp2

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template


###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    handler.response.out.write(html)


###############################################################################
# This function is for convenience - we'll use it to generate some general 
# page parameters.
def get_params():
    result = {}
    user = users.get_current_user()
    if user:
        result['logout_url'] = users.create_logout_url('/')
        result['user'] = user.email()
        result['upload_url'] = blobstore.create_upload_url('/upload')
    else:
        result['login_url'] = users.create_login_url()
    return result
  

###############################################################################
class MainHandler(webapp2.RequestHandler):
  def get(self):
    params = get_params()
    render_template(self, 'index.html', params)


###############################################################################
class ImagesHandler(webapp2.RequestHandler):
    def get(self):
        params = get_params()

        # first we retrieve the images for the current user
        q = MyImage.query(MyImage.user == params['user'])
        result = list()
        for i in q.fetch():
            # we append each image to the list
            result.append(i)
      
        # we will pass this image list to the template
        params['images'] = result
        render_template(self, 'images.html', params)


###############################################################################
class ImageHandler(webapp2.RequestHandler):
    def get(self):
        params = get_params()
    
        # we'll get the ID from the request
        image_id = self.request.get('id')
    
        # this will allow us to retrieve it from NDB
        my_image = ndb.Key(urlsafe=image_id).get()

        # we'll set some parameters and pass this to the template
        params['image_id'] = image_id
        params['image_name'] = my_image.name
        render_template(self, 'image.html', params)


###############################################################################
class FileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        params = get_params()
    
        if params['user']:
            upload_files = self.get_uploads()
            blob_info = upload_files[0]
            type = blob_info.content_type

            # we want to make sure the upload is a known type.
            if type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                name = self.request.get('name')
                my_image = MyImage()
                my_image.name = name
                my_image.user = params['user']

                # image is a BlobKeyProperty, so we will retrieve the key for this blob
                my_image.image = blob_info.key()
                my_image.put()
                image_id = my_image.key.urlsafe()
                self.redirect('/image?id=' + image_id)


###############################################################################
# note: you could also use images.get_serving_url here - that has 
# some arguments you could use directly.
#
# see https://cloud.google.com/appengine/docs/python/refdocs/google.appengine.api.images#google.appengine.api.images.get_serving_url
# for more details on this approach.
#
class ImageManipulationHandler(webapp2.RequestHandler):
    def get(self):

        image_id = self.request.get("id")
        my_image = ndb.Key(urlsafe=image_id).get()
        blob_key = my_image.image
        img = images.Image(blob_key=blob_key)

        modified = False

        h = self.request.get('height')
        w = self.request.get('width')
        fit = False

        if self.request.get('fit'):
            fit = True

        if h and w:
            img.resize(width=int(w), height=int(h), crop_to_fit=fit)
            modified = True

        optimize = self.request.get('opt')
        if optimize:
            img.im_feeling_lucky()
            modified = True

        flip = self.request.get('flip')
        if flip:
            img.vertical_flip()
            modified = True

        mirror = self.request.get('mirror')
        if mirror:
            img.horizontal_flip()
            modified = True

        rotate = self.request.get('rotate')
        if rotate:
            img.rotate(int(rotate))
            modified = True

        result = img
        if modified:
            result = img.execute_transforms(output_encoding=images.JPEG)

        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(result)


###############################################################################
class MyImage(ndb.Model):
    name = ndb.StringProperty()
    image = ndb.BlobKeyProperty()
    user = ndb.StringProperty()


###############################################################################
mappings = [
    ('/', MainHandler),
    ('/images', ImagesHandler),
    ('/image', ImageHandler),
    ('/upload', FileUploadHandler),
    ('/img', ImageManipulationHandler),
]
app = webapp2.WSGIApplication(mappings, debug=True)
