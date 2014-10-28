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

class SummaryMain(webapp2.RequestHandler):
  def get(self):
    user = self.request.get('user')
    month = self.request.get('month')
    transactions_query = Transaction.query()
    all_transactions = transactions_query.fetch(50)
    applicable_transactions = []
    for transaction in all_transactions:
      if transaction.owner_user_id == user:
        applicable_transactions.append(transaction)
        continue
      for share in transaction.share:
        if share.target == user:
          applicable_transactions.append(transaction)
          
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'months': months,
        'transactions': applicable_transactions,
        'url': url,
        'url_linktext': url_linktext,
    }

    template = JINJA_ENVIRONMENT.get_template('transactionlist.html')
    self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/summary', SummaryMain),
], debug=True)
