#! flask/bin/python
from flask.ext.login import LoginManager


login_manager = LoginManager()

login_manager.login_view ="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query(User.key(user_id))