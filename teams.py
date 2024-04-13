from sqlalchemy.sql import text
from db import db

def add_team(name):
    """Add a team into the database"""
    try:
        sql = text("INSERT INTO teams (name) VALUES (:name)")
        db.session.execute(sql, {"name":name})
        db.session.commit()
    except:
        return False
    return True

def add_player(player_id, team_id):
    """Add a player into the table documenting which players play for which teams"""
    try:
        sql = text("INSERT INTO team_players (player_id, team_id) VALUES (:player_id, :team_id)")
        db.session.execute(sql, {"player_id":player_id, "team_id":team_id})
        db.session.commit()
    except:
        return False
    return True

def move_player(player_id, team_id):
    """Move a player to another team"""
    try:
        sql = text("UPDATE team_players SET team_id=:team_id WHERE player_id=:player_id")
        db.session.execute(sql, {"player_id":player_id, "team_id":team_id})
        db.session.commit()
    except:
        return False
    return True

def show_teams():
    sql = text("SELECT id, name FROM teams")
    return db.session.execute(sql).fetchall()

def show_team(id):
    sql = text("SELECT id, name FROM teams WHERE id=:id")
    return db.session.execute(sql, {"id":id}).fetchone()

def list_players(team_id):
    sql = text("""SELECT P.id, P.name
               FROM players P 
               LEFT JOIN team_players TP ON P.id=TP.player_id 
               JOIN teams T ON T.id=TP.team_id
               AND T.id=:team_id
               """)
    return db.session.execute(sql, {"team_id":team_id}).fetchall()

def list_players_other(team_id):
    sql = text("""SELECT P.id, P.name, T.name
               FROM players P
               LEFT JOIN team_players TP ON P.id=TP.player_id
               JOIN teams T ON TP.team_id=T.id
               AND T.id!=:team_id
               ORDER BY P.name
               """)
    return db.session.execute(sql, {"team_id":team_id}).fetchall()

def record(team_id):
    sql = text("""SELECT
                        SUM(CASE WHEN (G.h_team_runs > G.a_team_runs AND G.h_team_id = :team_id)
                            OR (G.a_team_runs > G.h_team_runs AND G.a_team_id = :team_id) THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN (G.h_team_runs < G.a_team_runs AND G.h_team_id = :team_id)
                            OR (G.a_team_runs < G.h_team_runs AND G.a_team_id = :team_id) THEN 1 ELSE 0 END) AS losses
                    FROM
                        games G
                    JOIN
                        teams T ON T.id = :team_id;
               """)
    return db.session.execute(sql, {"team_id":team_id}).fetchone()