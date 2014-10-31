import os

from google.appengine.api import users

import json
import jinja2
import webapp2
from model import Month
from model import User
from model import Share
from model import Transaction

from datetime import date
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
    for user in all_users:
      if user.user_id:
        user_id_to_name[user.user_id] = user.display_name
    transactions_query = Transaction.query()
    transactions = transactions_query.fetch(50)
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'users': all_users,
        'user_id_to_name' : user_id_to_name,
        'months': months,
        'transactions': transactions,
        'url': url,
        'url_linktext': url_linktext,
    }

    template = JINJA_ENVIRONMENT.get_template('transactions.html')
    self.response.write(template.render(template_values))

class ListTransaction(webapp2.RequestHandler):
  def post(self):
    users_query = User.query()
    all_users = users_query.fetch(20)
    user_id_to_name = {}
    for user in all_users:
      if user.user_id:
        user_id_to_name[user.user_id] = user.display_name
    transactions_query = Transaction.query()
    transactions = transactions_query.fetch(50)

    self.response.headers['Content-Type'] = 'application/json'
    transaction_array = []
    for transaction in transactions:
      transaction_array.append(transactionToDict(transaction))
    result = {}
    result['rows'] = transaction_array
    self.response.write(json.dumps(result))

def transactionToDict(transaction):
  ui_transaction = {}
  ui_transaction['transaction_id'] = transaction.key().id()
  ui_transaction['payer'] = user_id_to_name[transaction.owner_user_id]
  ui_transaction['date'] = transaction.date.isoformat()
  ui_transaction['description'] = Transaction.description
  ui_transaction['total'] = Transaction.total
  return dict

application = webapp2.WSGIApplication([
    ('/transactions', TransactionsMain),
], debug=True)
