"""
This module contains the RequestHandlers to serve json responses needed by
the users page.
"""
from calendar import month

__author__ = 'jxc043100@gmail.com (Jiayun Chen)'

import os
from google.appengine.api import users
import jinja2
import webapp2
from google.appengine.ext import ndb
import json
import util
from model import User
from model import UserType


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class List(webapp2.RequestHandler):
  def post(self):
    user_array = []
    for user in util.getAllUsers():
      user_array.append(
                  {'id': user.user_id, 
                   'email': user.email, 
                   'display_name': user.display_name, 
                   'user_type': user.type.name, 
                   'registered':user.user_id > 0})
    result = {'rows': user_array, 'total': len(user_array)}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(result))
    
class Upsert(webapp2.RequestHandler):

    def post(self):
        current_user = users.get_current_user()
        display_name = self.request.get('display_name')
        email = self.request.get('email')
        user_type = self.request.get('user_type')
        user_key = ndb.Key(User, email)
        user = user_key.get()
        is_registration = user and (email == user.email) and not user.user_id
        if not user:
          user = User(id=email, email=email, display_name=display_name, type=UserType(user_type))
          user.put()
        else:
          user.display_name = display_name
          if (user_type):
            user.type = UserType(user_type)
          if is_registration:
            user.user_id = current_user.user_id()
          user.put()
        if is_registration:
          self.redirect('/transactions')
        else:
          self.response.write(json.dumps({}))

class Delete(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        if email:
          user_key = ndb.Key(User, email)
          user = user_key.get()
          user.key.delete()
        self.response.write(json.dumps({'success' : 1}))
        

application = webapp2.WSGIApplication([
    ('/user/list', List),
    ('/user/upsert', Upsert),
    ('/user/delete', Delete),
], debug=True)