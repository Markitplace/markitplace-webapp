# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

GEOCODE_URL ="https://maps.googleapis.com/maps/api/geocode/json?" 

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'


# mail server settings    
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['shookke@gmail.com']

# pagination
POSTS_PER_PAGE = 10

# search
MAX_SEARCH_RESULTS = 50

# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = 'shook_app_3510'
MS_TRANSLATOR_CLIENT_SECRET = 'SZEawxTl4wTvqEINGQQAu1GKt0TZuko+U++1FzFrbxA='

