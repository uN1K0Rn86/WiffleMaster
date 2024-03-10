from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)