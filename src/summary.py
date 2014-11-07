import os

from google.appengine.api import users

import jinja2
import webapp2
import util
from model import User
from model import Transaction


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
      paid = 0
      gained = 0
      if transaction.owner_user_id == user_id:
        paid = self.total_paid
      for share in transaction.share:
        if share.target == user_id:
          gained = paid / len(transaction.share)
        
      self.balance = paid - gained
  
class SummaryMain(webapp2.RequestHandler):
  def get(self):
    users_query = User.query()
    all_users = users_query.fetch(20)
    user_id_to_name = {}
    for user in all_users:
      if user.user_id:
        user_id_to_name[user.user_id] = user.display_name
        
    if users.get_current_user():
      user_email = users.get_current_user().email()
    current_user = users.get_current_user()
    user_id = self.request.get('user')
    if not user_id and current_user:
      user_id = current_user.user_id()
    month = self.request.get('month')
    transactions_query = Transaction.query()
    all_transactions = transactions_query.fetch(50)
    summary_entries = []
    for transaction in all_transactions:
      if transaction.owner_user_id == user_id:
        summary_entries.append(SummaryEntry(user_id, transaction))
        continue
      for share in transaction.share:
        if share.target == user_id:
          summary_entries.append(SummaryEntry(user_id, transaction))
     
    total_balance = 0      
    for summary_entry in summary_entries:
      total_balance +=summary_entry.balance

    template_values = {
        'user_id' : user_id,
        'user_id_to_name' : user_id_to_name,
        'entries': summary_entries,
        'total_balance' : total_balance,
        'header' : util.PageHeader(self.request.uri),
    }

    template = JINJA_ENVIRONMENT.get_template('summary.html')
    self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/summary', SummaryMain),
], debug=True)
