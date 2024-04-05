from sqlalchemy.sql import text
from db import db

def new_game(innings, a_team_id, h_team_id, league_id):
    try:
        sql = text("""INSERT INTO games (innings, a_team_id, h_team_id, a_team_runs, h_team_runs, league_id, in_progress, inning, game_time)
            VALUES (:innings, :a_team_id, :h_team_id, 0, 0, :league_id, TRUE, 1, NOW())
            RETURNING id""")
        id = db.session.execute(sql, {"innings":innings, "a_team_id":a_team_id, "h_team_id":h_team_id, "league_id":league_id}).fetchone()[0]
        db.session.commit()
    except:
        return False
    return id

def set_order(game_id, h_order, a_order, h_pitcher, a_pitcher):
    try:
        sql = text("""UPDATE games
                   SET h_order=:h_order, a_order=:a_order, h_pitcher=:h_pitcher, a_pitcher=:a_pitcher
                   WHERE id=:game_id
                   """)
        db.session.execute(sql, {"game_id":game_id, "h_order":h_order, "a_order":a_order, "h_pitcher":h_pitcher, "a_pitcher":a_pitcher})
        db.session.commit()
    except:
        return False
    return True

def get_h_order(id):
    sql = text("""SELECT h_order
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_a_order(id):
    sql = text("""SELECT a_order
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_h_pitcher(id):
    sql = text("""SELECT h_pitcher
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_a_pitcher(id):
    sql = text("""SELECT a_pitcher
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def away_team(id):
    sql = text("""SELECT G.a_team_id, T.name
            FROM games G, teams T
            WHERE G.id=:id
            AND G.a_team_id=T.id""")
    return db.session.execute(sql, {"id":id}).fetchone()

def home_team(id):
    sql = text("""SELECT G.h_team_id, T.name
            FROM games G, teams T
            WHERE G.id=:id
            AND G.h_team_id=T.id""")
    return db.session.execute(sql, {"id":id}).fetchone()

def total_innings(id):
    sql = text("""SELECT innings
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def current_inning(id):
    sql = text("""SELECT inning
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def runs_inning(game_id, inning):
    sql = text("""SELECT COALESCE(SUM(rbi), 0)
                FROM at_bats
                WHERE game_id=:game_id
                AND inning=:inning""")
    return db.session.execute(sql, {"game_id":game_id, "inning":inning}).fetchone()[0]

def runs_home(id):
    sql = text("""SELECT h_team_runs
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def runs_away(id):
    sql = text("""SELECT a_team_runs
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]
    
def batter_up(order, previous):
    if previous + 1 < len(order):
        return order[previous + 1]
    else:
        return order[0]
    
def batting_stats(game_id, player_id):
    sql = text("""SELECT 
                COALESCE(SUM(CASE WHEN result IN ('single', 'double', 'triple', 'HR') THEN 1 ELSE 0 END), 0) AS hits,
                COALESCE(SUM(CASE WHEN game_id=:game_id THEN 1 ELSE 0 END), 0) AS abs
                FROM at_bats
                WHERE batter_id=:player_id
               """)
    return db.session.execute(sql, {"player_id":player_id, "game_id":game_id}).fetchone()

class Game:
    def __init__(self, id, innings, home, away, league_id=None):
        self.id = id
        self.league_id = league_id
        self.innings = innings * 2
        self.home = home
        self.away = away
        self.inning = 1

    def play_inning(self):
        self.outs = 0

    def at_bat(self):
        self.strikes = 0
        self.swinging = 0
        self.balls = 0

    def pitch(self, result):
        if result == "strike":
            self.strikes += 1
        elif result == "swinging":
            self.strikes += 1
            self.swinging += 1
        elif result == "ball":
            self.balls += 1
        elif result == "single":
            pass