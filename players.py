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

def player_name(id):
    """Return the player's id and name"""
    sql = text("""SELECT id, name
               FROM players 
               WHERE id=:id
               """)
    return db.session.execute(sql, {"id":id}).fetchone()

def list_teamless():
    sql = text("""SELECT id, name FROM players WHERE id NOT IN
               (SELECT player_id FROM team_players)
               ORDER BY name""")
    return db.session.execute(sql).fetchall()

def batting_stats(player_id):
    sql = text("""SELECT
                        P.id AS id,
                        P.name AS name,
                        COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) AS pa,
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) AS walks,
                        COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) AS hits,
                        COALESCE(SUM(CASE WHEN A.result IN ('Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) AS xbh,
                        COALESCE(SUM(CASE WHEN A.result = 'Home Run' THEN 1 ELSE 0 END), 0) AS hr,
                        COALESCE(SUM(CASE WHEN A.result = 'Triple' THEN 1 ELSE 0 END), 0) AS triples,
                        COALESCE(SUM(CASE WHEN A.result = 'Double' THEN 1 ELSE 0 END), 0) AS doubles,
                        COALESCE(SUM(CASE WHEN A.result = 'Single' THEN 1 ELSE 0 END), 0) AS singles
                    FROM at_bats A, players P
                    WHERE A.batter_id = P.id
                    AND P.id=:player_id
                    GROUP BY P.id
               """)
    return db.session.execute(sql, {"player_id":player_id}).fetchone()