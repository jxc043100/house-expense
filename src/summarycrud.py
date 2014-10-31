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

class SummaryEntry:
  def __init__(self, user_id, transaction):
    self.user_id = user_id
    self.transaction = transaction
    self.date = transaction.date
    self.payer_id = transaction.owner_user_id
    self.description = transaction.description
    self.total_paid = transaction.total
    self.paid = 0
    self.gain = 0
    if transaction.owner_user_id == user_id:
      self.paid = self.total_paid
    for share in transaction.share:
      if share.target == user_id:
        self.gain = self.total_paid / len(transaction.share)
    self.balance = self.paid - self.gain
    
  def toUiEntry(self):
    ui_transaction = {}
    ui_transaction['payer'] = user_id_to_name[self.payer_id]
    ui_transaction['date'] = self.date.strftime('%m/%d/%Y')
    ui_transaction['description'] = self.description
    ui_transaction['total'] = self.total_paid
    ui_transaction['expense'] = self.paid
    ui_transaction['gain'] = self.gain
    ui_transaction['balance'] = self.balance
    return ui_transaction
      
class List(webapp2.RequestHandler):
  def post(self):
    current_user = users.get_current_user()
    if current_user:
      transactions_query = Transaction.query()
      transactions = transactions_query.fetch(50)
      summary_array = []
      total_owed = 0
      for transaction in transactions:
        if transaction.owner_user_id == current_user.user_id():
          summary_entry = SummaryEntry(current_user.user_id(), transaction)
          summary_array.append(summary_entry.toUiEntry())
          total_owed += summary_entry.balance
          continue
        for share in transaction.share:
          if share.target == current_user.user_id(): 
            summary_entry = SummaryEntry(current_user.user_id(), transaction)
            summary_array.append(summary_entry.toUiEntry())
            total_owed += summary_entry.balance  
      result = {}
      result['rows'] = summary_array
      result['total_owed'] = total_owed
      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(json.dumps(result))
    
class Pay(webapp2.RequestHandler):

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
        if not transaction_id:
          transaction = Transaction(owner_user_id=current_user.user_id(), description=description, total=total, date=time)
        else:
          transaction_key = ndb.Key(Transaction, int(transaction_id))
          transaction = transaction_key.get()
          transaction.description = description
          transaction.total = total
          transaction.date = time
        shares = []
        transaction.share = []
        for user_id in self.request.get_all('user_id'):
            shares.append(Share(target=user_id, share=1)) 
        transaction.share = shares
        transaction.put()
        self.response.write(json.dumps({}))

application = webapp2.WSGIApplication([
    ('/summary/list', List),
    ('/transaction/pay', Pay),
], debug=True)
