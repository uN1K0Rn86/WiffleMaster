from sqlalchemy.sql import text
from db import db

def add_player(name, bats, throws):
    """Add a player into the database."""
    try:
        sql = text("INSERT INTO players (name, bats, throws) VALUES (:name, :bats, :throws)")
        db.session.execute(sql, {"name":name, "bats":bats, "throws":throws})
        db.session.commit()
    except:
        return False
    return True

def display_players():
    """Return SQL query to display the first 5 players in alphabetical order."""
    sql = text("SELECT id, name, bats, throws FROM players ORDER BY name LIMIT 5")
    return db.session.execute(sql).fetchall()

def display_player(id):
    sql = text("SELECT name, bats, throws FROM players WHERE id=:id")
    return db.session.execute(sql, {"id":id}).fetchone()

def list_teamless():
    sql = text("""SELECT id, name FROM players WHERE id NOT IN
               (SELECT player_id FROM team_players)
               ORDER BY name""")
    return db.session.execute(sql).fetchall()