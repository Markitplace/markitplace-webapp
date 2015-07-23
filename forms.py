from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
	openid = StringField('openid', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)

from models import User
	
class EditForm(Form):
	body = StringField('body', validators=[DataRequired()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
	
	def __init__(self, original_body, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_body = original_body
		
	def validate(self):
		if not Form.validate(self):
			return False
		if self.body.data == self.original_body:
			return True
		if self.body.data != User.make_valid_nickname(self.body.data):
			sefl.body.errors.append(gettext('This body has invalid characters. Please use letters, numbers, dots and underscores only.'))
			return False
		user = User.query.filter_by(body=self.body.data).first()
		if user is not None:
			self.body.errors.append(gettext('This body is already in use. Please choose another one.'))
			return False
		return True
		
class PostForm(Form):
	post = StringField('post', validators=[DataRequired()])
	
class SearchForm(Form):
	search = StringField('search', validators=[DataRequired()])
	
class EditPost(Form):
	body = TextAreaField('body', validators=[Length(min=0, max=140)])