# server/main.py
from flask import Flask
from .database import init_db
from .auth_service import auth
from .file_service import file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/sharewave_db'
app.config['SECRET_KEY'] = 'your_secret_key'

init_db(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(file, url_prefix='/files')

@app.route('/')
def index():
    return "Welcome to ShareWave"

if __name__ == '__main__':
    app.run(debug=True)
