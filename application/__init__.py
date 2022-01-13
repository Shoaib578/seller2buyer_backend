from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_marshmallow import Marshmallow

import os
app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
app.config['SECRET_KEY'] = 'asjd9792nasd887a8dA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/seller2buyer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'admin.Login'
ma= Marshmallow(app)

db = SQLAlchemy(app)
Migrate(app,db)
from application.Admin.routes import admin
app.register_blueprint(admin)
from application.Apis.routes import apis
app.register_blueprint(apis,url_prefix='/apis')