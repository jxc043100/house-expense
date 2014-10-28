import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
from model import Month
from model import User
from datetime import date

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class AdminMain(webapp2.RequestHandler):

  def get(self):
    all_users = User.query().fetch()
    months_query = Month.query().order(-Month.start_date)
    months = months_query.fetch()
    
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'users': all_users,
        'months': months,
        'url': url,
        'url_linktext': url_linktext,
    }

    template = JINJA_ENVIRONMENT.get_template('admin.html')
    self.response.write(template.render(template_values))

class InviteUser(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        display_name = self.request.get('display_name')
        email = self.request.get('email')

        invited_user = User(id=email, email=email, display_name=display_name)
        invited_user.put()

        self.redirect('/admin')
        
class RegisterUser(webapp2.RequestHandler):
    def get(self):
      template_values = {}
      current_user = users.get_current_user()
      invited_user = None
      if current_user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        invited_user = User.get_by_id(current_user.email())

      else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
      template_values['url'] = url
      template_values['url_linktext'] = url_linktext
      template_values['invited_user'] = invited_user
      template_values['current_user'] = current_user
      template = JINJA_ENVIRONMENT.get_template('register.html')
      self.response.write(template.render(template_values))

    def post(self):
        current_user = users.get_current_user()
        if (current_user):
          display_name = self.request.get('display_name')
          user_key = ndb.Key(User, current_user.email())
          user = user_key.get()
          if user:
            user.user_id = current_user.user_id()
            user.display_name = display_name
            user.put()

        self.redirect('/transactions')

class DeleteUser(webapp2.RequestHandler):
    def post(self):
        user_key = ndb.Key(User, self.request.get('email'))
        user = user_key.get()
        if user:
          user.key.delete()

        self.redirect('/admin')
        
class CreateMonth(webapp2.RequestHandler):

    def post(self):
        display_name = self.request.get('display_name')
        year_string = self.request.get('year')
        month_string = self.request.get('month')
        start_date = date(int(year_string), int(month_string), 1)

        month = Month(id=year_string+ '/' +month_string)
        month.display_name = display_name
        month.start_date = start_date
        month.put()

        self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', AdminMain),
    ('/admin', AdminMain),
    ('/admin/createMonth', CreateMonth),
    ('/admin/inviteUser', InviteUser),
    ('/admin/deleteUser', DeleteUser),
    ('/register', RegisterUser),

], debug=True)
