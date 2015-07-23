from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from google.appengine.api import search
from random import SystemRandom
from bcrypt import bcrypt
from hashlib import md5



#! WHOOSH index Model
from app import app

import sys
if sys.version_info >= (3, 0):
	enable_search = False
else:
	enable_search = False
	import flask.ext.whooshalchemy as whooshalchemy

# Address Structured Propterty
class Address(ndb.Model):
	type = ndb.StringProperty()
	street = ndb.StringProperty()
	city = ndb.StringProperty()
	state = ndb.StringProperty()
	zip = ndb.IntegerProperty()
	loc = ndb.GeoPtProperty()
		

#! User Model
import re

class User(ndb.Model):
	nickname = ndb.StringProperty()
	fname = ndb.StringProperty()
	lname = ndb.StringProperty()
	email = ndb.StringProperty()
	pwd = ndb.StringProperty()
	about_me = ndb.StringProperty()
	last_seen = ndb.DateTimeProperty(auto_now_add=True)
	
	
	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

	def hash_pwd(self, pwd):
		self.pwd = bcrypt.hashpw(pwd, bcrypt.gensalt(1))
	
	def pwd_auth(self, pwd):
		if bcrypt.hashpw(pwd, self.pwd) == self.pwd:
			return True
				
	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
		
	def get_id(self):
		try:
			return self.key.id() # python 2
		except NameError:
			return self.key # python 3

	
	@staticmethod
	def make_valid_nickname(nickname):
		return re.sub('[^a-zA-Z0-9_\.]', '', nickname)
	
	@staticmethod
	def make_unique_nickname(nickname):
		if User.query(nickname=nickname) is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query(nickname=new_nickname) is None:
				break
			version += 1
		return new_nickname
			
	def __repr__(self):
		return '<User %r>' % (self.nickname)


#! Posts Model		
class Post(ndb.Model):
	body = ndb.StringProperty()
	timestamp = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
	author = ndb.KeyProperty(kind=User)
	language = ndb.StringProperty()
	
	def __repr__(self):
		return '<Post %r>' % (self.body)
		
		
class Followers(ndb.Model):
	followerid = ndb.KeyProperty(kind=User)
	followedid = ndb.KeyProperty(kind=User)
	
	'''
	def _pre_put_hook(self):
    	# inform someone they have new friend
	
	@classmethod
  	def _post_delete_hook(cls, key, future):
    	# inform someone they have lost a friend
	'''
		
#! Business Page Model
class Role(ndb.Model):
	role = ndb.IntegerProperty()
	user = ndb.KeyProperty(kind=User)

class Page(polymodel.PolyModel):
	category = ndb.StringProperty()
	admins = ndb.StructuredProperty(Role, repeated=True)
	name = ndb.StringProperty()
	addresses = ndb.StructuredProperty(Address, repeated=True)
	about = ndb.StringProperty()
	active = ndb.BooleanProperty(default=True)
	
	def __repr__(self):
		return '<BPage %r>' % (self.name)
	
class Nonprofit(Page):
	
	status = ndb.StringProperty()
	
class Business(Page):
	
	percentage = ndb.IntegerProperty()
	#reviews = ndb.KeyProperty(kind=Review)


if enable_search:
	whooshalchemy.whoosh_index(app, Post)
	
	