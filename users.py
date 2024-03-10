from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from db import db

def login(username, password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            return True
        else:
            return False
        
def logout():
    del session["user_id"]

def register(username, password):
    hash_value = generate_password_hash(password)
    print(hash_value)
    try:
        sql = text("INSERT INTO users (username,password) VALUES (:username,:password)")
        print("hi")
        db.session.execute(sql, {"username":username, "password":hash_value})
        print("yes")
        db.session.commit()
    except:
        return False
    return login(username, password)

def user_id():
    return session.get("user_id", 0)