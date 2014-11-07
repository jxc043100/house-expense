import os

from google.appengine.api import users

import json
import jinja2
import webapp2
import util
from model import TransactionType
from model import Transaction


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class TransactionsMain(webapp2.RequestHandler):
  def get(self):
    all_users = util.getAllUsers()
    transactions_query = Transaction.query()
    transactions = transactions_query.fetch(50)

    template_values = {
        'header' : util.PageHeader(self.request.uri),
        'users': all_users,
        'user_id_to_name' : util.getUserToDisplayNames(),
        'transactions': transactions,
        'transaction_types': [TransactionType.COMMON_FOOD, TransactionType.COMMON_CLEANING, TransactionType.NONRESIDENT, TransactionType.PERSONAL], 
    }

    template = JINJA_ENVIRONMENT.get_template('transactions.html')
    self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/transactions', TransactionsMain),
], debug=True)
