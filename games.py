from sqlalchemy.sql import text
from db import db

def new_game(innings, a_team_id, h_team_id, league_id):
    try:
        sql = text("""INSERT INTO games (innings, a_team_id, h_team_id, a_team_runs, h_team_runs, league_id, in_progress, inning, game_time)
            VALUES (:innings, :a_team_id, :h_team_id, 0, 0, :league_id, TRUE, 1, NOW())
            RETURNING id""")
        id = db.session.execute(sql, {"innings":innings, "a_team_id":a_team_id, "h_team_id":h_team_id, "league_id":league_id}).fetchone()[0]
        db.session.commit()
        print(id)
    except:
        return False
    return id

def away_team(id):
    sql = text("""SELECT a_team_id
            FROM games
            WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def home_team(id):
    sql = text("""SELECT h_team_id
            FROM games
            WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

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