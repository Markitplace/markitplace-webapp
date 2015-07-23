from hashlib import md5

from app import db


#! WHOOSH index Model
from app import app

import sys
if sys.version_info >= (3, 0):
	enable_search = False
else:
	enable_search = True
	import flask.ext.whooshalchemy as whooshalchemy

#!  Auxiliary table creation		
followers = db.Table('follower',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

'''
roles = db.Table('role',
	db.Column(db.Integer, primary_key=True)
	db.Column(db.Integer, db.ForeignKey('bpage.id')),
	db.Column(db.Integer, db.ForeignKey('npage.id')),
	db.Column(db.Integer, db.ForeignKey('user.id'))
'''

#! User Model
import re

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	followed = db.relationship('User',
								secondary=followers,
								primaryjoin=(followers.c.follower_id == id),
								secondaryjoin=(followers.c.followed_id == id),
								backref=db.backref('followers', lazy='dynamic'),
								lazy='dynamic')
	
	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)
	
	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
		
	def get_id(self):
		try:
			return unicode(self.id) # python 2
		except NameError:
			return str(self.id) # python 3

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self
	
	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self
	
	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0
		
	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())
	
	@staticmethod
	def make_valid_nickname(nickname):
		return re.sub('[^a-zA-Z0-9_\.]', '', nickname)
	
	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname
			
	def __repr__(self):
		return '<User %r>' % (self.nickname)


#! Posts Model		
class Post(db.Model):
	__searchable__ = ['body']
	
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	language = db.Column(db.String(5))
	
	def __repr__(self):
		return '<Post %r>' % (self.body)
		
#! Business Page Model
'''
class BPage(db.Model):
	__searchable__ = ['name']
	
	id = db.Column(db.Integer, primary_key=True)
	admins = db.relationship('roles', backref='admins', lazy='dynamic')
	name = db.Column(db.String(20))
	address = db.Column(db.String(40))
	about = db.Column(db.String(250))
	
	def __repr__(self):
		return '<BPage %r>' % (self.name)
	
class BPage(db.Model):
	__searchable__ = ['name']
	
	id = db.Column(db.Integer, primary_key=True)
	admins = db.relationship('roles', backref='admins', lazy='dynamic')
	name = db.Column(db.String(20))
	about = db.Column(db.String(250))
	
	def __repr__(self):
		return '<NPage %r>' % (self.name)	
'''

if enable_search:
	whooshalchemy.whoosh_index(app, Post)
	
	