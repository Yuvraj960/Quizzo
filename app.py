from flask import Flask
import os
from db_init import init_db

app = Flask(__name__)
app.secret_key = 'some_secret_key_for_session'
DATABASE = 'quiz_app.sqlite3'

if not os.path.exists(DATABASE):
    init_db()

from controllers.auth_controller import auth as auth_blueprint
from controllers.api_controller import api as api_blueprint
from controllers.admin_controller import admin as admin_blueprint
from controllers.user_controller import user as user_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(user_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
