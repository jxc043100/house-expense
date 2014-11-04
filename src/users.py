import os

from google.appengine.api import users

from google.appengine.ext import ndb
import json
import jinja2
import webapp2
from model import UserType
from model import User
from model import Transaction

from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Main(webapp2.RequestHandler):
  def get(self):
    user_email = ''
    if users.get_current_user():
        url = users.create_logout_url('/users')
        url_linktext = 'Logout'
        user_email = users.get_current_user().email()
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'You must login first'

    template_values = {
        'url': url,
        'url_linktext': url_linktext,
        'user_types': [UserType.ADMIN, UserType.NONRESIDENT, UserType.RESIDENT], 
        'user_email': user_email
    }

    template = JINJA_ENVIRONMENT.get_template('user.html')
    self.response.write(template.render(template_values))

class Register(webapp2.RequestHandler):
  def get(self):
    current_user = users.get_current_user()
    if current_user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        user_email = users.get_current_user().email()
        invited_user = User.get_by_id(current_user.email())

    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'You must login first'

    template_values = {
        'url': url,
        'url_linktext': url_linktext,
        'user_types': [UserType.ADMIN, UserType.NONRESIDENT, UserType.RESIDENT], 
        'user_email': user_email,
        'invited_user': invited_user
    }

    template = JINJA_ENVIRONMENT.get_template('register.html')
    self.response.write(template.render(template_values))
    
application = webapp2.WSGIApplication([
    ('/users', Main),
    ('/register', Register),
], debug=True)
