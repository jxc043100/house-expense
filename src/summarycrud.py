import os

from google.appengine.api import users

import jinja2
import webapp2
import util
from google.appengine.ext import ndb
import json
from model import User
from model import UserType
from model import Share
from model import Transaction
from model import TransactionType
from model import Month
import logging

from datetime import date
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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
    total_days = 0
    user_days = 0
    month = Month.get_by_id(self.date.strftime('%m/01/%Y'))
    user_id_to_email = util.getUserToEmail()
    for resident in month.residents:
        total_days += resident.days * resident.inhabitants
        if user_id_to_email[self.user_id] == resident.user_email:
            user_days = resident.days * resident.inhabitants
            
    num_inhabitants = util.getNumInhabitants(month)
    
    if transaction.owner_user_id == user_id:
      self.paid = self.total_paid
    if transaction.type == TransactionType.COMMON_FOOD:
        self.gain = self.total_paid * user_days / total_days
    if transaction.type == TransactionType.COMMON_CLEANING:
        self.gain = self.total_paid / num_inhabitants
    if transaction.type == TransactionType.NONRESIDENT:
        self.paid = self.total_paid * user_days / total_days
    elif transaction.type == TransactionType.PERSONAL:
        for share in transaction.share:
          if share.target == user_id:
              self.gain = self.total_paid / len(transaction.share)
    self.balance = self.paid - self.gain
    
  def toUiEntry(self, user_id_to_name):

    ui_transaction = {}
    ui_transaction['payer'] = user_id_to_name[self.payer_id]
    ui_transaction['date'] = self.date.strftime('%m/%d/%Y')
    ui_transaction['description'] = self.description
    ui_transaction['total'] = self.total_paid
    ui_transaction['expense'] = self.paid 
    ui_transaction['gain'] = self.gain
    ui_transaction['balance'] = self.balance
    ui_transaction['transaction_type'] = self.transaction.type.name
    if self.transaction.type == TransactionType.PERSONAL:
      ui_transaction['user'] = user_id_to_name[self.transaction.share[0].target]
    return ui_transaction
  
class List(webapp2.RequestHandler):
  def post(self):
    user_id = self.request.get('user_id')
    user_id_to_name = util.getUserToDisplayNames()
    current_user = users.get_current_user()
    if current_user and not user_id:
      user_id = current_user.user_id()
    transactions = util.getTransactions(self.request.get('month'))
    summary_array = []
    total_owed = 0
    for transaction in transactions:
      if isApplicableTransaction(transaction, user_id, self.request.get('month')):
        summary_entry = SummaryEntry(user_id, transaction)
        summary_array.append(summary_entry.toUiEntry(user_id_to_name))
        total_owed += summary_entry.balance
    result = {}
    result['rows'] = summary_array
    result['total'] = len(summary_array)
    result['footer'] = [{"description":"Total Balance: " + str(total_owed)}]
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(result))
    
def isApplicableTransaction(transaction, user_id, month_id):
    if transaction.type == TransactionType.NONRESIDENT:
        return True
    if transaction.owner_user_id == user_id:
        return True
    for share in transaction.share:
        if share.target == user_id:
            return True
    if (transaction.type == TransactionType.COMMON_CLEANING or transaction.type == TransactionType.COMMON_FOOD) \
        and util.isUserResident(user_id, month_id):
        return True
    return False

class ListUsers(webapp2.RequestHandler):
  def post(self):
    current_user = users.get_current_user()
    combo_array = []
    for user in util.getAllUsers():
      if user.type == UserType.RESIDENT or user.type == UserType.ADMIN:
        user_dict = {'id' :user.user_id, 'text' : user.display_name}
        if current_user and current_user.user_id() == user.user_id:
          user_dict['selected'] = True
        combo_array.append(user_dict)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(combo_array))
      
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

class MonthlySummary(webapp2.RequestHandler):
    
    def post(self):
        summaries = []
        months = util.getMonths()
        transactions_query = Transaction.query()
        transactions = transactions_query.fetch(50)
        
        for month in months:
            month_begin = datetime.strptime(month['id'],"%m/%d/%Y")
            month_end = datetime(month_begin.year + (month_begin.month / 12), ((month_begin.month % 12) + 1), 1)
            num_inhabitants = util.getNumInhabitants(month)
            
            sum_food_cost = 0
            for transaction in transactions:
                if transaction.type == TransactionType.COMMON_FOOD and transaction.date >= month_begin and transaction.date < month_end:
                    sum_food_cost += transaction.total
            sum_utility_cost = 0
            for transaction in transactions:
                if transaction.type == TransactionType.COMMON_CLEANING and transaction.date >= month_begin and transaction.date < month_end:
                    sum_utility_cost += transaction.total
            summaries.append({'month' : month['text'],
                              'food_cost_per_person' : sum_food_cost / num_inhabitants if num_inhabitants > 0 else 0,
                              'utility_cost_per_person' : sum_utility_cost / num_inhabitants if num_inhabitants > 0 else 0})
        
        self.response.write(json.dumps(summaries))
application = webapp2.WSGIApplication([
    ('/summary/list', List),
    ('/summary/listUsers', ListUsers),
    ('/transaction/pay', Pay),
    ('/summary/monthly', MonthlySummary),
], debug=True)
