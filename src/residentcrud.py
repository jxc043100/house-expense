import os
from google.appengine.api import users
import jinja2
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext import db
import json
import util
from model import User
from model import Resident
from model import Month
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class List(webapp2.RequestHandler):
    def post(self):
        residents_array = []
        month_id = self.request.get('search_month')
        if not month_id:
            month_id = datetime(datetime.today().year, datetime.today().month, 1).strftime('%m/%d/%Y')
        month = Month.get_by_id(month_id)
        for resident in month.residents:
            residents_array.append(
                {'email': resident.user_email, 
                'display_name': User.get_by_id(resident.user_email).display_name,
                'days': resident.days,
                'month': month.name,
                'id' : month.key.id(),
                'inhabitants' : resident.inhabitants})
        result = {'rows': residents_array, 'total': len(residents_array)}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(result))

class ListResidentOptions(webapp2.RequestHandler):
    def post(self):
        residents_array = []
        month_id = self.request.get('search_month')
        if not month_id:
            month_id = datetime(datetime.today().year, datetime.today().month, 1).strftime('%m/%d/%Y')
        month = Month.get_by_id(month_id)
        for resident in month.residents:
            residents_array.append(
                {
                 'id': resident.user_id, 
                 'text': User.get_by_id(resident.user_email).display_name
                })
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(residents_array))
        
class Upsert(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        days = self.request.get('days')
        month = Month.get_by_id(self.request.get('month'))
        inhabitants = self.request.get('inhabitants')
        resident = None
        
        for listed_resident in month.residents:
            if listed_resident.user_email == email:
                resident = listed_resident
        if resident:
            resident.days = int(days)
            resident.inhabitants = int(inhabitants)
            month.put()
            self.response.write(json.dumps({}))
        else:
            resident = Resident(user_email=email, days=int(days), 
                                user_id=User.get_by_id(email).user_id, 
                                inhabitants=int(inhabitants))
            month.residents.append(resident)
            month.put()
            self.response.write(json.dumps({}))
        
        
class Delete(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        month = Month.get_by_id(self.request.get('month'))
        if email:
            for resident in month.residents:
                if resident.user_email == email:
                    month.residents.remove(resident)
                    month.put()
                    break
        self.response.write(json.dumps({'success' : 1}))
        
class ListMonths(webapp2.RequestHandler):
    def post(self):
        addMonth()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(util.getMonths()))

def addMonth():
    months = util.getMonths()
    current_month = Month.get_by_id(months[0]['id'])
    last_month = Month.get_by_id(months[1]['id'])
    if not current_month:
        month_to_add = Month(id=months[0]['id'], name=months[0]['text'], residents = [])
        if last_month:
            for resident in last_month.residents:
                month_to_add.residents.append(resident)
        month_to_add.put()

application = webapp2.WSGIApplication([
    ('/resident/list', List),
    ('/resident/upsert', Upsert),
    ('/resident/delete', Delete),
    ('/resident/listMonths', ListMonths),
    ('/resident/listOptions', ListResidentOptions)
], debug=True)