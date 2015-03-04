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

def getUserToEmail():
    all_users = getAllUsers()
    user_id_to_email = {}
    for user in all_users:
        if user.user_id:
            user_id_to_email[user.user_id] = user.email
    return user_id_to_email

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
        self.is_admin = users.is_current_user_admin()
        if invited_user:
            self.type = invited_user.type.name
    else:
        self.url = users.create_login_url(current_uri)
        self.url_linktext = 'You must login first'
        self.logged_in = False
        self.user_email = ''
    
def getTransactions(month_begin_str=False):
    if month_begin_str:
        month_begin = datetime.strptime(month_begin_str,"%m/%d/%Y")
    else:
        month_begin = datetime(datetime.today().year, datetime.today().month, 1)
    month_end = datetime(month_begin.year + (month_begin.month / 12), ((month_begin.month % 12) + 1), 1)
    transactions_query = Transaction.query(ndb.AND(Transaction.date >= month_begin,Transaction.date < month_end))
    transactions_query.order(Transaction.date)    
    return transactions_query.fetch()

def getMonths():
  months_array = []
  start_date = datetime.strptime("09-01-2014","%m-%d-%Y")
  month = datetime.today().month
  year = datetime.today().year
  month_to_add = datetime(year, month, 1)
  months_array.append({'id' : month_to_add.strftime('%m/%d/%Y'), 
                       'text' : month_to_add.strftime('%B %Y'),
                       'selected' : True})
  while month_to_add > start_date:
    year = year - 1 if month == 1 else year
    month = 12 if month == 1 else month - 1
    month_to_add = datetime(year, month, 1)
    months_array.append({'id' : month_to_add.strftime('%m/%d/%Y'), 
                         'text' : month_to_add.strftime('%B %Y')})
  return months_array
