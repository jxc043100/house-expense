import os

from google.appengine.api import users

from google.appengine.ext import ndb
import json
import jinja2
import webapp2
from model import UserType
from model import User
from model import Transaction
from model import TransactionType

from datetime import datetime

def can_view(transaction, user):
  if user.type == UserType.ADMIN:
    return True
  else:
    return transaction.type != TransactionType.RENT
