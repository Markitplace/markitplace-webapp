from google.appengine.ext import ndb
from config import GEOCODE_URL
from app import app
import urllib2
import json

def getKey(kind, key):
  key = ndb.Key(kind, key)
  return key.get()

def callback(post):
  acct = getKey('User', post.author.id())
  return post, acct
  
def getGeo(address):
  add = urllib2.quote(address)
  req_url = GEOCODE_URL + "address=%s&sensor=false&region=us" % add
  req = urllib2.urlopen(req_url)
  jsonResponse = json.loads(req.read())
  return jsonResponse['results'][0]['geometry']['location']

def serialize(model):
  qry = model.query(model.name == 'Nsync') # fetching every instance of model
  page = qry.get()
  loc = page.addresses[0].loc
  return  page, loc