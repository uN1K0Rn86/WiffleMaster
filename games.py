from sqlalchemy.sql import text
from db import db
import at_bats

def new_game(innings, a_team_id, h_team_id, league_id):
    """Add a game into the database."""
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
    """Return a boolean determining whether a game is in progress or not."""
    sql = text("""SELECT in_progress
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def latest(count):
    """Return the results of the determined number of latest games."""
    sql = text("""SELECT G.id AS id,
                         G.a_team_runs AS a_runs,
                         TA.name AS a_team,
                         G.h_team_runs AS h_runs,
                         TH.name AS h_team,
                         G.game_time AS time
                    FROM
                        games G
                    JOIN
                        teams TA ON G.a_team_id = TA.id
                    JOIN
                        teams TH ON G.h_team_id = TH.id
                    ORDER BY
                        G.game_time DESC
                    LIMIT
                        :count
               """)
    return db.session.execute(sql, {"count":count}).fetchall()

def games_in_progress():
    """Return a list of games that are in progress."""
    sql = text("""SELECT G.id AS id,
                         G.a_team_runs AS a_runs,
                         TA.name AS a_team,
                         G.h_team_runs AS h_runs,
                         TH.name AS h_team,
                         G.h_order AS h_order,
                         G.a_order AS a_order
                    FROM
                        games G
                    JOIN
                        teams TA ON G.a_team_id = TA.id
                    JOIN
                        teams TH ON G.h_team_id = TH.id
                    WHERE
                        G.in_progress = true
                    ORDER BY
                        G.game_time DESC
               """)
    return db.session.execute(sql).fetchall()

def set_order(game_id, h_order, a_order, h_pitcher, a_pitcher):
    """Update the table games with batting orders and starting pitchers."""
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
    """Return the batting order for the home team."""
    sql = text("""SELECT h_order
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_a_order(id):
    """Return the batting order for the away team."""
    sql = text("""SELECT a_order
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_h_pitcher(id):
    """Return the id of the pitcher for the home team."""
    sql = text("""SELECT h_pitcher
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def get_a_pitcher(id):
    """Return the id for the pitcher for the away team."""
    sql = text("""SELECT a_pitcher
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def away_team(id):
    """Return the away team's id and name for a given game."""
    sql = text("""SELECT G.a_team_id, T.name
            FROM games G, teams T
            WHERE G.id=:id
            AND G.a_team_id=T.id""")
    return db.session.execute(sql, {"id":id}).fetchone()

def home_team(id):
    """Return the home team's id and name for a given game."""
    sql = text("""SELECT G.h_team_id, T.name
            FROM games G, teams T
            WHERE G.id=:id
            AND G.h_team_id=T.id""")
    return db.session.execute(sql, {"id":id}).fetchone()

def total_innings(id):
    """Return the total number of innings for a given game."""
    sql = text("""SELECT innings
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def current_inning(id):
    """Return the current inning for a given game."""
    sql = text("""SELECT inning
               FROM games
               WHERE id=:id""")
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def runs_inning(game_id, inning):
    """Return the amount of runs scored in a given inning in a given game."""
    sql = text("""SELECT COALESCE(SUM(rbi), 0)
                FROM at_bats
                WHERE game_id=:game_id
                AND inning=:inning
                """)
    return db.session.execute(sql, {"game_id":game_id, "inning":inning}).fetchone()[0]

def runs_home(id):
    """Return the total amount of runs scored by the home team in a given game."""
    sql = text("""SELECT h_team_runs
               FROM games
               WHERE id=:id
               """)
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def runs_away(id):
    """Return the total amount of runs scored by the away team in a given game."""
    sql = text("""SELECT a_team_runs
               FROM games
               WHERE id=:id
               """)
    return db.session.execute(sql, {"id":id}).fetchone()[0]

def hits_home(game_id):
    """Return the total number of hits by the home team in a given game."""
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
    """Return the total number of hits by the away team in a given game."""
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
    """Return the id and name of the current batter."""
    if previous + 1 < len(order):
        return order[previous + 1]
    else:
        return order[0]
    
def get_h_previous(game_id):
    """Return the index of the previous batter for the home team.
       This is used to determine the current batter."""
    sql = text("""SELECT h_previous
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def set_h_previous(game_id, previous):
    """Set the index (in the batting order) of the previous batter."""
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
    """Return the index of the previous batter for the away team.
       This is used to determine the current batter."""
    sql = text("""SELECT a_previous
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def set_a_previous(game_id, previous):
    """Set the index (in the batting order) of the previous batter."""
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
    """Return batting stats for a player in a given game."""
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
    """Change the home team's pitcher in a given game."""
    try:
        ab_id = at_bats.current_ab_id(game_id)
        sql = text("""UPDATE games
                SET h_pitcher=:player_id
                WHERE id=:game_id
                """)
        sql2 = text("""UPDATE at_bats
                    SET pitcher_id=:player_id
                    WHERE id=:ab_id
                    """)
        db.session.execute(sql, {"game_id":game_id, "player_id":player_id})
        db.session.execute(sql2, {"ab_id":ab_id, "player_id":player_id})
        db.session.commit()
    except:
        return False
    return True

def change_a_pitcher(game_id, player_id):
    """Change the away team's pitcher in a given game."""
    try:
        ab_id = at_bats.current_ab_id(game_id)
        sql = text("""UPDATE games
                SET a_pitcher=:player_id
                WHERE id=:game_id
                """)
        sql2 = text("""UPDATE at_bats
                    SET pitcher_id=:player_id
                    WHERE id=:ab_id
                    """)
        db.session.execute(sql, {"game_id":game_id, "player_id":player_id})
        db.session.execute(sql2, {"ab_id":ab_id, "player_id":player_id})
        db.session.commit()
    except:
        return False
    return True

def get_outs(game_id):
    """Return the current amount of outs in a given game."""
    sql = text("""SELECT outs
               FROM games
               WHERE id=:game_id
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def add_out(game_id):
    """Add an out to the given game. Advance to the next inning if it is the third out.
       If it is the final out of the game, call the finish game function."""
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
        if get_outs(game_id) == 3:
            finish_game(game_id)
    except:
        return False
    return True

def get_runners(game_id):
    """Return a list of runners who are currently on base."""
    sql = text("""SELECT R.id, R.status
               FROM runners R
               JOIN games G ON R.game_id=G.id
               WHERE G.id=:game_id
                 AND R.status IN (1, 2, 3)
               ORDER BY R.status
               """)
    return db.session.execute(sql, {"game_id":game_id}).fetchall()

def parse_option(value):
    """Parse a string from a form and return a list with integers."""
    parts = value.split("_")
    parts[0] = parts[0][1:]
    parts[1] = parts[1][:1]
    id = int(parts[0])
    status = int(parts[1])
    return [id, status]

def add_runner(ab_id, game_id, status):
    """Add a new runner."""
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
    """Update (advance or out) the runners."""
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
    """Add scored runs."""
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
    """Set the game's in_progress status to false."""
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
    """Return the amount of pitches thrown by a given pitcher in a given game."""
    sql = text("""SELECT SUM(strikes+balls+fouls) AS pitches
               FROM at_bats
               WHERE game_id=:game_id
               AND pitcher_id=:pitcher_id
               """)
    return db.session.execute(sql, {"game_id":game_id, "pitcher_id":pitcher_id}).fetchone()[0]