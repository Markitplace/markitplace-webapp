from flask.ext.wtf import Form
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, PasswordField, SelectField
from wtforms.validators import Email, InputRequired, DataRequired, ValidationError, Length


class LoginForm(Form):
	email = StringField('Email', validators=[InputRequired(), Email()])
	password = PasswordField('Password', validators=[InputRequired()])
	remember_me = BooleanField('remember_me', default=False)


class RegistrationForm(Form):
	nickname = StringField("Display Name")
	fname = StringField('First Name', validators=[InputRequired()])
	lname = StringField('Last Name', validators=[InputRequired()])
	email = StringField('Email address', validators=[InputRequired(), Email()])
	password = PasswordField('Password', validators=[InputRequired()])

from app.models import User
from flask.ext.babel import gettext
	
class EditForm(Form):
	nickname = StringField('nickname', validators=[DataRequired()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
	
	def __init__(self, original_body, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_body = original_body.nickname
		
	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_body:
			return True
		if self.nickname.data != User.make_valid_nickname(self.nickname.data):
			sefl.body.errors.append(gettext('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
			return False
		user = User.query(User.nickname==self.nickname.data)
		if user is not None:
			self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
			return False
		return True
		
class PostForm(Form):
	post = StringField('post', validators=[DataRequired()])
	
class SearchForm(Form):
	search = StringField('search', validators=[DataRequired()])
	
class EditPost(Form):
	body = TextAreaField('body', validators=[Length(min=0, max=140)])
	
class CreatePageForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	
class CreateBusPageForm(CreatePageForm):
	category = SelectField('Choose a category', choices=[('Restaraunt','Restaraunt'),('Retail','Retail')])
	street = StringField('Street Address', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	zipcode = IntegerField('Zipcode', validators=[DataRequired()])
	percentage = IntegerField('Percentage you want to give', validators=[DataRequired()])

	
	