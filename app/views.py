from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, make_response
from flask.ext.login import login_user, logout_user, current_user, login_required
from guess_language import guessLanguage
from flask.ext.babel import gettext
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES
from app import app, db, login_manager, oid, babel
from ms_translate import microsoft_translate
from .forms import LoginForm, RegistrationForm, EditForm, PostForm, SearchForm, CreateBusPageForm
from .models import User, Post, Business, Nonprofit, Address, Role, Page
from .emails import follower_notification
from .fetch import callback, getKey, getGeo, serialize
from google.appengine.ext import ndb
from google.appengine.api import search


@login_manager.user_loader
def load_user(key):
	return User.get_by_id(key)
		
@babel.localeselector
def get_locale():
	return request.accept_languages.best_match(LANGUAGES.keys())
	#return 'es'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
	form = PostForm()
	if form.validate_on_submit():
		language = guessLanguage(form.post.data)
		if language == 'UNKNOWN' or len(language) > 5:
			language = ''
		post = Post(body=form.post.data,
					timestamp=datetime.utcnow(),
					parent=g.user.key,
					author=g.user.key,
					language=language)
		post.put()
		flash(gettext('Your post is now live!'))
		return redirect(url_for('index'))
	#posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	page,loc = serialize(Page)
	pages = {
           'name':  str(page.name),
		   'lat': loc.lat,
		   'lon': loc.lon
       }
	return render_template('index.html',
							title='Home',
							form=form,
							pages=pages)
							#posts=posts)
							
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		u = User.query(User.email==form.email.data)
		user = u.get()
		if user.pwd_auth(form.password.data):
			session['remember_me'] = form.remember_me.data
			if 'remember_me' in session:
				remember_me = session['remember_me']
				session.pop('remember_me', None)
			login_user(user, remember = remember_me)
			return redirect(request.args.get('next') or url_for('index'))
		else:
			flash(gettext("Invalid email or password"))
			return redirect(url_for('login'))
	return render_template('login.html',
							title='Sign In',
							form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		g.user.put()
		g.search_form = SearchForm()
	g.locale = get_locale()
						
@oid.after_login
def after_login(resp):
	if  resp.email is None or resp.email == "":
		flash(gettext('Invalid login. Please try again.'))
		return redirect(url_for('login'))
	user = User.query(User.email==resp.email)
	if user is None:
		flash(gettext('No user found.'))
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))
						
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegistrationForm()
	if form.validate_on_submit():# and User.query(email=form.email.data)==None:
		user = User(nickname=form.nickname.data,
					fname=form.fname.data,
					lname=form.lname.data,
					email=form.email.data)
		user.hash_pwd(form.password.data)
		user.put()
		flash(gettext('Signup Successful!'))
		return redirect(url_for('index'))
	return render_template('signup.html', form=form)

# User page 	
@app.route('/user/<nickname>', methods=['GET', 'POST'])
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
@login_required
def user(nickname, page=1):
	form = PostForm()
	if form.validate_on_submit():
		language = guessLanguage(form.post.data)
		if language == 'UNKNOWN' or len(language) > 5:
			language = ''
		post = Post(body=form.post.data,
					timestamp=datetime.utcnow(),
					parent=g.user.key,
					author=g.user.key,
					language=language)
		post.put()
		flash(gettext('Your post is now live!'))
		return redirect(url_for('user', nickname=nickname))
	key = User.query(User.nickname == nickname)
	user = key.get()
	if user == None:
		flash(gettext('User %(nickname)s not found.', nickname = nickname))
		return redirect(url_for('index'))
	qry = Post.query(ancestor=user.key).order(-Post.timestamp)
	posts = qry.map(callback)
	return render_template('user.html',
							user=user,
							form=form,
							posts=posts)
							
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user)
	if form.validate_on_submit():
		key = User.query(User.nickname==g.user.nickname)
		g.user = key.get()
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		g.user.put()
		flash(gettext('Your changes have been saved.'))
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)
	
@app.route('/follow/<nickname>')
def follow(nickname):
	qry = User.query(User.nickname==nickname)
	user = qry.get()
	if user is None:
		flash(gettext('User %(nickname)s not found.', nickname = nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash(gettext('Cannot follow %(nickname)s.', nickname = nickname))
		return redirect(url_for('index', nickname=nickname))	
	u = g.user.follow(user)
	if u is None:
		flash(gettext('Cannot follow %(nickname)s.', nickname = nickname))
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You are now following %(nickname)s!', nickname = nickname))
	follower_notification(user, g.user)
	return redirect(url_for('user', nickname=nickname))
	
@app.route('/unfollow/<nickname>')
def unfollow(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash(gettext('User %(nickname)s not found.', nickname = nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash(gettext('You can\'t unfollow yourself!'))
		return redirect(url_for('self', nickname=nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash(gettext('Cannot unfollow %(nickname)s.', nickname = nickname))
		return redirect(url_for('user', nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash(gettext('You have stopped following %(nickname)s.', nickname = nickname))
	return redirect(url_for('user', nickname=nickname))
	
@app.route('/site_search', methods=['POST'])
@login_required
def site_search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	index = search.Index('Post')
	querystring = query
	try:
  		search_query = search.Query(
      		query_string=querystring,
      		options=search.QueryOptions(
          	limit=10))
  		results = index.search(search_query)
		return render_template('search_results.html',
							query=query,
							results=results)
	except search.Error:
		 flash(search.Error)
	
							
@app.route('/translate', methods=['POST'])
@login_required
def translate():
	return jsonify({
		'text': microsoft_translate(
			request.form['text'],
			request.form['sourceLang'],
			request.form['destLang']) })

# Post Edit takes POST request, updates database, and sends response back to client			
@app.route('/postEdit', methods=['POST'])
@login_required
def postEdit():
	key = request.form['id']
	qry = ndb.Key(urlsafe=key)
	post = qry.get()
	post.body = request.form['body']
	post.put()
	resp = make_response('{"test": "ok"}')
	resp.headers['Content-Type'] = "application/json"
	return resp
			
@app.route('/delete/<id>')
@login_required
def delete(id):
	key = ndb.Key(urlsafe=id)
	post = key.get()
	if post is None:
		flash(gettext('Post not found.'))
		return redirect(url_for('index'))
	if post.author != g.user.key:
		flash(gettext('You cannot delete this post.'))
		return redirect(url_for('index'))
	post.key.delete()
	flash(gettext('Your post has been deleted.'))
	return redirect(url_for('user', nickname=g.user.nickname))
	
@app.route('/create_business_page', methods=['GET', 'POST'])
@login_required
def create_business_page():
	form = CreateBusPageForm()
	if form.validate_on_submit():
		address = form.street.data + ' ' + form.city.data + ', ' + form.state.data + ' ' + str(form.zipcode.data)
		loc = getGeo(address)
		loc = ndb.GeoPt(loc['lat'],loc['lng'])
		business = Business(name=form.name.data,
					admins=[Role(role=1,
								user=g.user.key)],
					category=form.category.data,
					addresses=[Address(street=form.street.data,
										city=form.city.data,
										state=form.state.data,
										zip=form.zipcode.data,
										loc=loc)])
		business.put()
		flash(gettext('Page Successfully Created!'))
		return redirect(url_for('index'))
	else:
		flash(gettext('Something went wrong.'))
	return render_template('create_page.html', form=form, pageType='business')
	
@app.route('/page/<name>', methods=['GET', 'POST'])
def page(name):
	key = Page.query(Page.name == name)
	page = key.get()
	if page == None:
		flash(gettext('The %(name) page not found.', name = name))
		return redirect(url_for('index'))
	return render_template('page.html',
							page=page)
	
@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404
	
@app.errorhandler(500)
def internal_error(error):
	return render_template('500.html'), 500

from flask.ext.sqlalchemy import get_debug_queries

@app.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= DATABASE_QUERY_TIMEOUT:
			app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statment, query.parameters, query.duration, query.context))
	return response