from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

# Inicijaliziraj Flask aplikaciju
app = Flask(__name__)

# Učitaj konfiguraciju iz okoline ili koristi zadane vrijednosti
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/sharewave')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

# Inicijaliziraj ekstenzije
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Učitaj modele
from . import models

# Učitaj rute
from . import auth_service, file_service, main

# Stvori bazu podataka ako ne postoji
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
