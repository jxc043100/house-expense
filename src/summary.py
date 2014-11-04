import os

from google.appengine.api import users

import jinja2
import webapp2
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
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'user_id' : user_id,
        'user_id_to_name' : user_id_to_name,
        'months': months,
        'entries': summary_entries,
        'total_balance' : total_balance,
        'url': url,
        'url_linktext': url_linktext,
        'user_email': user_email if user_email else '',
    }

    template = JINJA_ENVIRONMENT.get_template('summary.html')
    self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/summary', SummaryMain),
], debug=True)
