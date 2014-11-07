import os

from google.appengine.api import users

from google.appengine.ext import ndb
import json
import jinja2
import webapp2
import util
from model import UserType
from model import User

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Main(webapp2.RequestHandler):
  def get(self):

    template_values = {
        'header' : util.PageHeader(self.request.uri),
        'user_types': [UserType.ADMIN, UserType.NONRESIDENT, UserType.RESIDENT], 
    }

    template = JINJA_ENVIRONMENT.get_template('user.html')
    self.response.write(template.render(template_values))

class Register(webapp2.RequestHandler):
  def get(self):
    invited_user = None
    current_user = users.get_current_user()
    if current_user:
        invited_user = User.get_by_id(current_user.email())

    template_values = {
        'header' : util.PageHeader(self.request.uri),
        'user_types': [UserType.ADMIN, UserType.NONRESIDENT, UserType.RESIDENT], 
        'invited_user': invited_user
    }

    template = JINJA_ENVIRONMENT.get_template('register.html')
    self.response.write(template.render(template_values))
    
application = webapp2.WSGIApplication([
    ('/users', Main),
    ('/register', Register),
], debug=True)
