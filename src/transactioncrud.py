"""
This module contains the RequestHandlers to serve json responses needed by
the transaction page.
"""

import os
from google.appengine.api import users
import jinja2
import webapp2
from google.appengine.ext import ndb
import json
from model import Share
from model import Transaction
from model import TransactionType
from model import UserType
from datetime import datetime
import util

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ListTransaction(webapp2.RequestHandler):
  def post(self):
    month_begin_str = self.request.get('month')
    if month_begin_str:
      month_begin = datetime.strptime(month_begin_str,"%m/%d/%Y")
    else:
      month_begin = datetime(datetime.today().year, datetime.today().month, 1)
    month_end = datetime(month_begin.year + (month_begin.month / 12), ((month_begin.month % 12) + 1), 1)
    user_id_to_name = util.getUserToDisplayNames()
    transactions_query = Transaction.query()
    transactions = transactions_query.fetch(50)

    transaction_array = []
    for transaction in transactions:
      if transaction.owner_user_id in user_id_to_name.keys():
        if transaction.date >= month_begin and transaction.date < month_end:
          transaction_array.append(transactionToDict(transaction, user_id_to_name))
    result = {'rows' : transaction_array, 'total' : len(transaction_array)}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(result))
    
class ListMonths(webapp2.RequestHandler):
  def post(self):
    months_array = []
    start_date = datetime.strptime("09-01-2014","%m-%d-%Y")
    month = datetime.today().month
    year = datetime.today().year
    month_to_add = datetime(year, month, 1)
    months_array.append({'id' : month_to_add.strftime('%m/%d/%Y'), 
                         'text' : month_to_add.strftime('%B %Y'),
                         'selected' : True})
    while month_to_add > start_date:
      month = 12 if month == 1 else month - 1
      year = year - 1 if month == 1 else year
      month_to_add = datetime(year, month, 1)
      months_array.append({'id' : month_to_add.strftime('%m/%d/%Y'), 
                           'text' : month_to_add.strftime('%B %Y')})
  
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(months_array))

def transactionToDict(transaction, user_id_to_name):
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
        elif (transaction.type == TransactionType.COMMON_FOOD or 
              transaction.type == TransactionType.COMMON_CLEANING or 
              transaction.type == TransactionType.NONRESIDENT):
          for user in util.getAllUsers():
            if user.type == UserType.ADMIN or user.type == UserType.RESIDENT:
              shares.append(Share(target=user.user_id, share=1)) 
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
    ('/transaction/listMonths', ListMonths),
], debug=True)
