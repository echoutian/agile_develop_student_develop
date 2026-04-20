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
@app.context_processor
def static_file_url():
	from flask import url_for

	def static_file(filename):
		try:
			fullpath = os.path.join(app.static_folder, filename)
			if os.path.exists(fullpath):
				v = int(os.path.getmtime(fullpath))
				return url_for('static', filename=filename, v=v)
		except Exception:
			pass
		return url_for('static', filename=filename)

	return dict(static_file=static_file)
