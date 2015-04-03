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
import re

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ListTransaction(webapp2.RequestHandler):
    def post(self):
        user_id_to_name = util.getUserToDisplayNames()
        transactions = util.getTransactions(self.request.get('month'))
        transaction_array = []
        for transaction in transactions:
            transaction_array.append(transactionToDict(transaction, user_id_to_name))
        result = {'rows' : transaction_array, 'total' : len(transaction_array)}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(result))
    
class ListMonths(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(util.getMonths()))

def transactionToDict(transaction, user_id_to_name):
  ui_transaction = {}
  ui_transaction['transaction_id'] = str(transaction.key.id())
  ui_transaction['payer'] = user_id_to_name[transaction.owner_user_id]
  ui_transaction['payer_id'] = transaction.owner_user_id
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
        p = re.compile('\d+')
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
          if not p.match(target_user):
            return
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
    ('/transaction/listMonths', ListMonths),
], debug=True)
