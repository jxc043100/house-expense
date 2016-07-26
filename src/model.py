from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop

class UserType(messages.Enum):
  RESIDENT = 1
  NONRESIDENT = 2
  ADMIN = 3
  
class User(ndb.Model):
  """Models a user invited to use the app."""
  user_id = ndb.StringProperty(indexed=True)
  email = ndb.StringProperty(indexed=True)
  display_name = ndb.StringProperty(indexed=False)
  admin = ndb.BooleanProperty(indexed=True)
  type = msgprop.EnumProperty(UserType, required=True)
  
class Share(ndb.Model):
  """Models a target and what portion of the cost is counted for this person."""
  target = ndb.StringProperty(indexed=True)
  
  # portion counted to this individual
  share = ndb.IntegerProperty(indexed=False)
  dollar_portion = ndb.FloatProperty(indexed=False)
  
class TransactionType(messages.Enum):
  COMMON_FOOD = 1
  PERSONAL = 2
  RENT = 3
  PAYMENT = 4
  NONRESIDENT = 5
  COMMON_CLEANING = 6
  
  
class Transaction(ndb.Model):
  """Models a transaction amount in which the owner paid for others."""
  owner_user_id = ndb.StringProperty(indexed=True)
  type = msgprop.EnumProperty(TransactionType, required=True)
  date = ndb.DateTimeProperty()
  description = ndb.StringProperty(indexed=True)
  total = ndb.FloatProperty(indexed=False)
  share = ndb.StructuredProperty(Share, repeated=True)

class Resident(ndb.Model):
  user_id = ndb.StringProperty()
  user_email = ndb.StringProperty()
  days = ndb.IntegerProperty()
  inhabitants = ndb.IntegerProperty(default=1)

class Month(ndb.Model):
  residents = ndb.StructuredProperty(Resident, repeated=True)
  name = ndb.StringProperty()
  