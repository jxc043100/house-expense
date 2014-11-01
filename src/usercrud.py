import os

from google.appengine.api import users

import jinja2
import webapp2
from google.appengine.ext import ndb
import json
from model import User
from model import UserType
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

start_date = datetime.strptime("08-01-2014","%m-%d-%Y")
month = datetime.today().month
year = datetime.today().year
months = []
month_to_add = datetime(year, month, 1)
users_query = User.query()
all_users = users_query.fetch(20)
user_id_to_name = {}
for user in all_users:
  if user.user_id:
    user_id_to_name[user.user_id] = user.display_name
        
while month_to_add > start_date:
  months.append(month_to_add)
  if (month == 1):
    month = 12
    year = year -1
  else:
    month = month - 1
  month_to_add = datetime(year, month, 1)

class List(webapp2.RequestHandler):
  def post(self):
    users_query = User.query()
    all_users = users_query.fetch(20)
    
    user_array = []
    for user in all_users:
      user_dict = {'id': user.user_id, 'email': user.email, 'display_name': user.display_name, 'user_type': user.type.name}
      user_array.append(user_dict)
    result = {}
    result['rows'] = user_array
    result['total'] = len(user_array)
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(result))
    
class Upsert(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        current_user = users.get_current_user()
        display_name = self.request.get('display_name')
        email = self.request.get('email')
        user_type = self.request.get('user_type')
        user_key = ndb.Key(User, current_user.email())
        user = user_key.get()
        if not user:
          user = User()
        if current_user.email == email:
          user.user_id = current_user.user_id()
        user.display_name = display_name
        user.type = UserType(user_type)
        user.email = self.request.get('email')
        user.put()
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
