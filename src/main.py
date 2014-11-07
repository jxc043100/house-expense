import os

from google.appengine.api import users

import json
import jinja2
import webapp2
import util

from google.appengine.ext import ndb
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
    current_user = users.get_current_user()
    user = None
    if current_user:
      user_key = ndb.Key(User, current_user.email())
      user = user_key.get()
      if user and user.user_id:
          self.redirect('/transactions')
      if user and not user.user_id:
          self.redirect('/register')

    template_values = {
        'header' : util.PageHeader(self.request.uri),
        'user' : user,
    }

    template = JINJA_ENVIRONMENT.get_template('main.html')
    self.response.write(template.render(template_values))
    
application = webapp2.WSGIApplication([
    ('/', Main),
], debug=True)
