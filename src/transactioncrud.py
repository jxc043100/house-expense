import os

from google.appengine.api import users

import jinja2
import webapp2
from google.appengine.ext import ndb
import json
from model import Month
from model import User
from model import Share
from model import Transaction
from model import TransactionType
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
    result['total'] = len(transaction_array)
    self.response.write(json.dumps(result))
    
def transactionToDict(transaction):
  ui_transaction = {}
  ui_transaction['transaction_id'] = str(transaction.key.id())
  ui_transaction['payer'] = user_id_to_name[transaction.owner_user_id]
  ui_transaction['date'] = transaction.date.strftime('%m/%d/%Y')
  ui_transaction['description'] = transaction.description
  ui_transaction['total'] = transaction.total
  ui_transaction['transaction_type'] = transaction.type.name
  if transaction.type == TransactionType.PERSONAL:
    ui_transaction['user'] = user_id_to_name[transaction.share[0].target]
      
  return ui_transaction
    
class UpsertTransaction(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        current_user = users.get_current_user()
        description = self.request.get('description')
        total = float(self.request.get('total'))
        time = datetime.strptime(self.request.get('date'),"%m/%d/%Y")
        transaction_id = self.request.get('transaction_id')
        type = self.request.get('transaction_type')
        target_user = self.request.get('user')
        if not transaction_id:
          transaction = Transaction(owner_user_id=current_user.user_id(), description=description, total=total, date=time, type = TransactionType(type))
        else:
          transaction_key = ndb.Key(Transaction, int(transaction_id))
          transaction = transaction_key.get()
          transaction.description = description
          transaction.total = total
          transaction.type = TransactionType(type)
          transaction.date = time
        shares = []
        transaction.share = []
        if transaction.type == TransactionType.PERSONAL:
          shares.append(Share(target=target_user, share=1)) 
        transaction.share = shares
        transaction.put()
        self.response.write(json.dumps({}))

class DeleteTransaction(webapp2.RequestHandler):

    def post(self):
        transaction_id = self.request.get('transaction_id')
        if transaction_id:
          transaction = Transaction.get_by_id(int(transaction_id))
          transaction.key.delete()
        self.response.write(json.dumps({'success' : 1}))

application = webapp2.WSGIApplication([
    ('/transaction/list', ListTransaction),
    ('/transaction/upsert', UpsertTransaction),
    ('/transaction/delete', DeleteTransaction),
], debug=True)
