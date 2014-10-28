import os

from google.appengine.api import users

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

    template = JINJA_ENVIRONMENT.get_template('transactionlist.html')
    self.response.write(template.render(template_values))

class UpsertTransaction(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        current_user = users.get_current_user()
        description = self.request.get('description')
        total = float(self.request.get('total'))
        time = datetime.strptime(self.request.get('date'),"%m-%d-%Y")
        new_transaction = Transaction(owner_user_id=current_user.user_id(), description=description, total=total, date=time)
        shares = []
        for user_id in self.request.get_all('user_id'):
            shares.append(Share(target=user_id, share=1)) 
        new_transaction.share = shares
        new_transaction.put()
        self.redirect('/transactions')
        
class DeleteTransaction(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        display_name = self.request.get('display_name')
        year_string = self.request.get('year')
        month_string = self.request.get('month')
        start_date = date(int(year_string), int(month_string), 1)

        month = Month(id=year_string+ '/' +month_string)
        month.display_name = display_name
        month.start_date = start_date
        month.put()

        self.redirect('/')

application = webapp2.WSGIApplication([
    ('/transactions', TransactionsMain),
    ('/transactions/upsert', UpsertTransaction),
    ('/transactions/delete', DeleteTransaction),
], debug=True)
