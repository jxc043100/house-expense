"""
This module contains all the RequestHandlers to serve the all the HTML pages.
Each RequestHandler populates the jinja template dictionary, and renders
the jinja HTML template.
"""

__author__ = 'jxc043100@gmail.com (Jiayun Chen)'

import os
import jinja2
import webapp2
import util
from google.appengine.api import users
from google.appengine.ext import ndb
from model import UserType
from model import User
from model import TransactionType
from model import Month

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Main(webapp2.RequestHandler):
  """Main page at '/'. 
  Will render the header and redirect to relevant pages,
  or display information that the user is not registered or not logged in.
  """
  
  def get(self):
    current_user = users.get_current_user()
    user = None
    if current_user:
      user_key = ndb.Key(User, current_user.email())
      user = user_key.get()
      if user and user.user_id:
          self.redirect('/transactions')
          return
      if user and not user.user_id:
          self.redirect('/register')
          return

    template_values = {
        'header' : util.PageHeader(self.request.uri),
        'user' : user,
    }

    template = JINJA_ENVIRONMENT.get_template('main.html')
    self.response.write(template.render(template_values))
    
class UsersPage(webapp2.RequestHandler):
  """users listing page at '/users'. 
  Will render the users table.
  """
  
  def get(self):
    header = util.PageHeader(self.request.uri)
    
    if not header.logged_in:
        self.redirect('/')
        return
    
    template_values = {
        'header' : header,
        'user_types': [UserType.ADMIN, UserType.NONRESIDENT, UserType.RESIDENT], 
    }
    

    template = JINJA_ENVIRONMENT.get_template('user.html')
    self.response.write(template.render(template_values))

class RegisterPage(webapp2.RequestHandler):
  """Registration page at '/register'. 
  Will render a form to prompt the user to register.
  """
  
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

class TransactionsPage(webapp2.RequestHandler):
  """Transactions page at '/transactions'. 
  Will render the transactions table
  """
  
  def get(self):
    header = util.PageHeader(self.request.uri)
    
    if not header.logged_in:
      self.redirect('/')
      return
  
    template_values = {
        'header' : header,
        'user_id_to_name' : util.getUserToDisplayNames(),
        'current_user_id' : users.get_current_user().user_id(),
        'current_user_is_admin' : header.is_admin
    }
    

    if not header.invited_user or header.invited_user.type == UserType.NONRESIDENT:
      template_values['transaction_types'] = [TransactionType.NONRESIDENT]
    else:
      template_values['transaction_types'] = [TransactionType.COMMON_FOOD, 
                                              TransactionType.COMMON_CLEANING, 
                                              TransactionType.NONRESIDENT, 
                                              TransactionType.PERSONAL]

    template = JINJA_ENVIRONMENT.get_template('transactions.html')
    self.response.write(template.render(template_values))

class SummaryPage(webapp2.RequestHandler):
  """Summary page at '/summary'. 
  Will render the summary table
  """
  
  def get(self):
    header = util.PageHeader(self.request.uri)
    
    if not header.logged_in:
        self.redirect('/')
        return
    
    template_values = {
        'user_id_to_name' : util.getUserToDisplayNames(),
        'header' : header,
    }

    template = JINJA_ENVIRONMENT.get_template('summary.html')
    self.response.write(template.render(template_values))

class MonthlySummaryPage(webapp2.RequestHandler):
  """Monthly Summary page at '/monthlysummary'. 
  Will render the monthly summary table
  """
  
  def get(self):
    header = util.PageHeader(self.request.uri)
    
    if not header.logged_in:
        self.redirect('/')
        return
    
    template_values = {
        'user_id_to_name' : util.getUserToDisplayNames(),
        'header' : header,
    }

    template = JINJA_ENVIRONMENT.get_template('monthlysummary.html')
    self.response.write(template.render(template_values))

class ResidentsPage(webapp2.RequestHandler):
    
  def get(self):
    header = util.PageHeader(self.request.uri)
    
    if not header.logged_in:
        self.redirect('/')
        return
    
    template_values = {
        'user_id_to_name' : util.getUserToDisplayNames(),
        'header' : header,
        'users' : util.getAllUsers(),
        'months' : util.getMonths(),
    }

    template = JINJA_ENVIRONMENT.get_template('residents.html')
    self.response.write(template.render(template_values))


    
application = webapp2.WSGIApplication([
    ('/', Main),
    ('/summary', SummaryPage),
    ('/transactions', TransactionsPage),
    ('/users', UsersPage),
    ('/register', RegisterPage),
    ('/monthlysummary', MonthlySummaryPage),
    ('/residents', ResidentsPage),
], debug=True)

