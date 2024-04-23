from sqlalchemy.sql import text
from db import db

def add_league(name):
    """Add a league into the database"""
    try:
        sql = text("INSERT INTO leagues (name) VALUES (:name)")
        db.session.execute(sql, {"name":name})
        db.session.commit()
    except:
        return False
    return True

def add_team(team_id, league_id):
    """Add a team into a league"""
    try:
        sql = text("INSERT INTO league_teams (team_id, league_id) VALUES (:team_id, :league_id)")
        db.session.execute(sql, {"team_id":team_id, "league_id":league_id})
        db.session.commit()
    except:
        return False
    return True

def show_leagues():
    """Return a list of leagues in the database."""
    sql = text("SELECT id, name FROM leagues")
    return db.session.execute(sql).fetchall()

def show_league(league_id):
    """Return a league's id and name."""
    sql = text("""SELECT id, name FROM leagues
               WHERE id=:league_id""")
    return db.session.execute(sql, {"league_id":league_id}).fetchone()

def show_teams(league_id):
    """Return a list of teams in the league"""
    sql = text("""SELECT T.id, T.name
                FROM teams T
                LEFT JOIN league_teams LT
                ON T.id=LT.team_id
                JOIN leagues L
                ON L.id=LT.league_id
                AND L.id=:league_id
                """)
    return db.session.execute(sql, {"league_id":league_id}).fetchall()

def show_other_teams(league_id):
    """Return a list of teams not in the league"""
    sql = text("""SELECT T.id, T.name
               FROM teams T
               WHERE T.id
               NOT IN (SELECT T.id
                FROM teams T
                LEFT JOIN league_teams LT
                ON T.id=LT.team_id
                JOIN leagues L
                ON L.id=LT.league_id
                AND L.id=:league_id)
               """)
    return db.session.execute(sql, {"league_id":league_id}).fetchall()

def league_table(league_id):
    """Return wins and losses for all teams in this league."""
    sql = text("""SELECT
                        T.id AS id,
                        T.name AS name,
                        SUM(CASE WHEN (G.h_team_runs > G.a_team_runs AND G.h_team_id = T.id)
                            OR (G.a_team_runs > G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN (G.h_team_runs < G.a_team_runs AND G.h_team_id = T.id)
                            OR (G.a_team_runs < G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END) AS losses,
                        SUM(CASE WHEN (G.h_team_runs > G.a_team_runs AND G.h_team_id = T.id)
                            OR (G.a_team_runs > G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END) /
                            (SUM(CASE WHEN (G.h_team_runs > G.a_team_runs AND G.h_team_id = T.id)
                            OR (G.a_team_runs > G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END) +
                            SUM(CASE WHEN (G.h_team_runs < G.a_team_runs AND G.h_team_id = T.id)
                            OR (G.a_team_runs < G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END)) AS win_pct
                    FROM
                        games G
                    JOIN
                        leagues L ON G.league_id = L.id
                        AND L.id = :league_id
                    JOIN
                        teams T ON G.h_team_id = T.id OR G.a_team_id = T.id
                    WHERE
                        G.in_progress = false
                    GROUP BY
                        T.id
                    ORDER BY
                        win_pct DESC
               """)
    return db.session.execute(sql, {"league_id":league_id}).fetchall()