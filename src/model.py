from google.appengine.ext import ndb


def transaction_key(entry_id):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Purchase', entry_id)

class User(ndb.Model):
  user_id = ndb.StringProperty(indexed=True)
  email = ndb.StringProperty(indexed=True)
  display_name = ndb.StringProperty(indexed=False)
  admin = ndb.BooleanProperty(indexed=True)
  
class Month(ndb.Model):
  display_name = ndb.StringProperty(indexed=False)
  start_date = ndb.DateProperty(indexed=True)
  
class Share(ndb.Model):
  """Models a target and what portion of the cost is counted for this person."""
  target = ndb.StringProperty(indexed=True)
  
  # portion counted to this individual
  share = ndb.IntegerProperty(indexed=False)
  dollar_portion = ndb.FloatProperty(indexed=False)
  
class Transaction(ndb.Model):
  """Models a transaction amount in which the owner paid for others."""
  owner_user_id = ndb.StringProperty(indexed=True)
  date = ndb.DateTimeProperty()
  description = ndb.StringProperty(indexed=True)
  total = ndb.FloatProperty(indexed=False)
  share = ndb.StructuredProperty(Share, repeated=True)

    
    
    
    
    
    
    
    
    
    
    
    
    
    