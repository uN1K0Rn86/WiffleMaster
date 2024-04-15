from sqlalchemy.sql import text
from db import db
import at_bats

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

def in_progress(game_id):
    sql = text("""SELECT in_progress
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def games_in_progress():
    sql = text("""SELECT G.id AS id,
                         G.a_team_runs AS a_runs,
                         TA.name AS a_team,
                         G.h_team_runs AS h_runs,
                         TH.name AS h_team
                    FROM
                        games G
                    JOIN
                        teams TA ON G.a_team_id = TA.id
                    JOIN
                        teams TH ON G.h_team_id = TH.id
                    WHERE
                        G.in_progress = true;
               """)
    return db.session.execute(sql).fetchall()

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
                AND inning=:inning
                """)
    return db.session.execute(sql, {"game_id":game_id, "inning":inning}).fetchone()[0]

def runs_home(id):
    sql = text("""SELECT h_team_runs
               FROM games
               WHERE id=:id
               """)
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def runs_away(id):
    sql = text("""SELECT a_team_runs
               FROM games
               WHERE id=:id
               """)
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def hits_home(game_id):
    sql = text("""SELECT COUNT(*)
               FROM at_bats A
               JOIN GAMES G
               ON A.game_id=G.id
               AND A.b_team_id=G.h_team_id
               AND A.result IN ('Single', 'Double', 'Triple', 'Home Run')
               AND A.game_id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def hits_away(game_id):
    sql = text("""SELECT COUNT(*)
               FROM at_bats A
               JOIN GAMES G
               ON A.game_id=G.id
               AND A.b_team_id=G.a_team_id
               AND A.result IN ('Single', 'Double', 'Triple', 'Home Run')
               AND A.game_id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]
    
def batter_up(order, previous):
    if previous + 1 < len(order):
        return order[previous + 1]
    else:
        return order[0]
    
def get_h_previous(game_id):
    sql = text("""SELECT h_previous
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def set_h_previous(game_id, previous):
    try:
        sql = text("""UPDATE games
                SET h_previous=:previous
                WHERE id=:game_id
                """)
        db.session.execute(sql, {"previous":previous, "game_id":game_id})
        db.session.commit()
    except:
        return False
    return True

def get_a_previous(game_id):
    sql = text("""SELECT a_previous
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def set_a_previous(game_id, previous):
    try:
        sql = text("""UPDATE games
                SET a_previous=:previous
                WHERE id=:game_id
                """)
        db.session.execute(sql, {"previous":previous, "game_id":game_id})
        db.session.commit()
    except:
        return False
    return True
    
def batting_stats(game_id, player_id):
    sql = text("""SELECT 
                COALESCE(SUM(CASE WHEN result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) AS hits,
                COALESCE(SUM(CASE WHEN game_id=:game_id AND result NOT IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) AS abs
                FROM at_bats
                WHERE batter_id=:player_id
                AND game_id=:game_id
                AND result IS NOT NULL
               """)
    return db.session.execute(sql, {"player_id":player_id, "game_id":game_id}).fetchone()

def change_h_pitcher(game_id, player_id):
    try:
        sql = text("""UPDATE games
                SET h_pitcher=:player_id
                WHERE id=:game_id
                """)
        db.session.execute(sql, {"game_id":game_id, "player_id":player_id})
        db.session.commit()
    except:
        return False
    return True

def change_a_pitcher(game_id, player_id):
    try:
        sql = text("""UPDATE games
                SET a_pitcher=:player_id
                WHERE id=:game_id
                """)
        db.session.execute(sql, {"game_id":game_id, "player_id":player_id})
        db.session.commit()
    except:
        return False
    return True

def get_outs(game_id):
    sql = text("""SELECT outs
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def add_out(game_id):
    try:
        inning = current_inning(game_id)
        total = total_innings(game_id)*2
        if get_outs(game_id) == 2 and (inning != total or runs_away(game_id) == runs_home(game_id)):
            lob(game_id)
            sql = text("""UPDATE games
                    SET outs = 0, inning = inning + 1
                    WHERE id=:game_id
                    """)
        elif get_outs(game_id) == 2 and inning >= total and inning % 2 == 0 and runs_away(game_id) != runs_home(game_id):
            sql = text("""UPDATE games
                       SET outs = 3
                       WHERE id=:game_id
                       """)
        else:
            sql = text("""UPDATE games
                       SET outs = outs + 1
                       """)
        db.session.execute(sql, {"game_id":game_id})
        db.session.commit()
        if get_outs(game_id) == 0 and inning >= total and runs_home(game_id) > runs_away(game_id):
            finish_game(game_id)
        if get_outs(game_id) == 3 and inning >= total and inning % 2 == 0 and runs_away(game_id) != runs_home(game_id):
            finish_game(game_id)
    except:
        return False
    return True

def get_runners(game_id):
    sql = text("""SELECT R.id, R.status
               FROM runners R
               JOIN games G ON R.game_id=G.id
               WHERE G.id=:game_id
                 AND R.status IN (1, 2, 3)
               ORDER BY R.status
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchall()

def parse_option(value):
    parts = value.split("_")
    parts[0] = parts[0][1:]
    parts[1] = parts[1][:1]
    id = int(parts[0])
    status = int(parts[1])
    return [id, status]

def add_runner(ab_id, game_id, status):
    runner_id = at_bats.current_batter(ab_id)
    if current_inning(game_id) % 2 == 1:
        pitcher_id = get_h_pitcher(game_id)
    else:
        pitcher_id = get_a_pitcher(game_id)
    try:
        sql = text("""INSERT INTO runners (runner_id, pitcher_id, game_id, status)
                VALUES (:runner_id, :pitcher_id, :game_id, :status)
                """)
        db.session.execute(sql, {"runner_id":runner_id, "pitcher_id":pitcher_id, "game_id":game_id, "status":status})
        db.session.commit()
    except:
        return False
    return True

def update_runners(game_id, runners):
    try:
        if runners == []:
            return True
        for runner in runners:
            sql = text("""UPDATE runners
                       SET status=:status
                       WHERE id=:id
                       AND game_id=:game_id
                       """)
            db.session.execute(sql, {"status":runner[1], "id":runner[0], "game_id":game_id})
            db.session.commit()
    except:
        return False
    return True

def lob(game_id):
    """Sets the runners' status to 5 (left on base) if the inning ends"""
    try:
        sql = text("""UPDATE runners
                    SET status=5
                    WHERE game_id=:game_id
                    """)
        db.session.execute(sql, {"game_id":game_id})
        db.session.commit()
    except:
        return False
    return True

    

def add_runs(game_id, runs):
    try:
        if current_inning(game_id) % 2 == 1:
            sql = text("""UPDATE games
                    SET a_team_runs = a_team_runs + :runs
                    WHERE id=:game_id
                    """)
        else:
            sql = text("""UPDATE games
                    SET h_team_runs = h_team_runs + :runs
                    WHERE id=:game_id
                    """)
        db.session.execute(sql, {"game_id":game_id, "runs":runs})
        db.session.commit()
    except:
        return False
    return True

def finish_game(game_id):
    try:
        sql = text("""UPDATE games
                   SET in_progress=false
                   WHERE id=:game_id
                   """)
        db.session.execute(sql, {"game_id":game_id})
        db.session.commit()
    except:
        return False
    return True

def pitch_count(game_id, pitcher_id):
    sql = text("""SELECT SUM(strikes+balls+fouls) AS pitches
               FROM at_bats
               WHERE game_id=:game_id
               AND pitcher_id=:pitcher_id
               """)
    return db.session.execute(sql, {"game_id":game_id, "pitcher_id":pitcher_id}).fetchone()[0]