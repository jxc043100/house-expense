import os

from google.appengine.api import users

from google.appengine.ext import ndb
import json
import jinja2
import webapp2
from model import UserType
from model import User
from model import Transaction
from model import TransactionType
from model import Month

from datetime import datetime

def can_view(transaction, user):
  if user.type == UserType.ADMIN:
    return True
  else:
    return transaction.type != TransactionType.RENT
  
def getUserToDisplayNames():
  all_users = getAllUsers()
  user_id_to_name = {}
  for user in all_users:
    if user.user_id:
      user_id_to_name[user.user_id] = user.display_name
  return user_id_to_name

def getAllUsers():
  users_query = User.query()
  return users_query.fetch(20)

def getAllMonths():
  months_query = Month.query()
  return months_query.fetch(20)

class PageHeader():
  def __init__(self, current_uri):
    current_user = users.get_current_user()
    if current_user:
        self.url = users.create_logout_url('/users')
        self.url_linktext = 'Logout'
        self.logged_in = True
        self.user_email = current_user.email()
        self.is_admin = users.is_current_user_admin()
        invited_user = User.get_by_id(current_user.email())
        self.invited_user = invited_user
        if invited_user:
            self.type = invited_user.type.name
    else:
        self.url = users.create_login_url(current_uri)
        self.url_linktext = 'You must login first'
        self.logged_in = False
        self.user_email = ''
    
