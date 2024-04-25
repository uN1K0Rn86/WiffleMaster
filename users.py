from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
import secrets
from db import db


def login(username, password):
    """Check the username and password.
    If they match, create a session and return True.
    Else, return False.
    """
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["csrf_token"] = secrets.token_hex(16)
            return True
        else:
            return False
        
def logout():
    """Delete the user session."""
    del session["user_id"]

def register(username, password):
    """Generate a password hash value.
    Insert the username and password hash into the database.
    Return False if the process fails.
    Log the user in if registration is successful.
    """
    hash_value = generate_password_hash(password)
    print(hash_value)
    try:
        sql = text("INSERT INTO users (username,password) VALUES (:username,:password)")
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_id():
    """Return the user_id."""
    return session.get("user_id", 0)