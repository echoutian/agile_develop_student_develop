from flask_wtf.csrf import CSRFProtect
from flask import Flask
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
app = Flask(__name__)
login=LoginManager(app)
csrf = CSRFProtect(app)
login.login_view ='login'


app.config.from_object(Config)
UPLOAD_FOLDER=os.path.join(app.root_path,'uploads')
db= SQLAlchemy(app)

os.makedirs(UPLOAD_FOLDER,exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from app import routes,models