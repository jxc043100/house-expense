import os

from google.appengine.api import users

import json
import jinja2
import webapp2
from model import TransactionType
from model import User
from model import Transaction

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

while month_to_add > start_date:
  months.append(month_to_add)
  if (month == 1):
    month = 12
    year = year -1
  else:
    month = month - 1
  month_to_add = datetime(year, month, 1)

class TransactionsMain(webapp2.RequestHandler):
  def get(self):
    users_query = User.query()
    all_users = users_query.fetch(20)
    user_id_to_name = {}
    user_email = ''
    for user in all_users:
      if user.user_id:
        user_id_to_name[user.user_id] = user.display_name
    transactions_query = Transaction.query()
    transactions = transactions_query.fetch(50)
    if users.get_current_user():
        user_email = users.get_current_user().email()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'You must login first'

    template_values = {
        'users': all_users,
        'user_id_to_name' : user_id_to_name,
        'months': months,
        'transactions': transactions,
        'transaction_types': [TransactionType.COMMON_FOOD, TransactionType.COMMON_CLEANING, TransactionType.NONRESIDENT, TransactionType.PERSONAL, TransactionType.RENT], 
        'url': url,
        'url_linktext': url_linktext,
        'user_email': user_email
    }

    template = JINJA_ENVIRONMENT.get_template('transactions.html')
    self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/transactions', TransactionsMain),
], debug=True)
