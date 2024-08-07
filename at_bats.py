from sqlalchemy.sql import text
from db import db
import games
import ab_helpers

def pitch_results():
    """Return a list of possible results for any pitch."""
    return ["Intentional Walk", "Single", "Double", "Triple", "Home Run", "Groundout", "Flyout", "Lineout", "Fielder's choice", "Sac fly", "Sac bunt",
            "Single (out)", "Double (out)", "Triple (out)"]

def create_at_bat(game_id, batter_id, pitcher_id, b_team_id, p_team_id):
    """Create a new at bat."""
    outs = games.get_outs(game_id)
    inning = games.current_inning(game_id)
    try:
        sql = text("""INSERT INTO at_bats (batter_id, pitcher_id, outs, inning, p_team_id, b_team_id, game_id)
               VALUES (:batter_id, :pitcher_id, :outs, :inning, :p_team_id, :b_team_id, :game_id)
               """)
        db.session.execute(sql, {"batter_id":batter_id, "pitcher_id":pitcher_id, "outs":outs, "inning":inning,
                                      "p_team_id":p_team_id, "b_team_id":b_team_id, "game_id":game_id})
        db.session.commit()
    except:
        return False
    return True

def current_ab_id(game_id):
    """Return the id of the current at bat, or None if there is no current at bat."""
    inning = games.current_inning(game_id)
    if inning % 2 == 1:
        sql = text("""SELECT A.id
                FROM at_bats A
                JOIN games G
                   ON A.game_id = G.id
                WHERE A.game_id=:game_id
                AND A.b_team_id=G.a_team_id
                AND result IS NULL
                ORDER BY A.id DESC
                LIMIT 1
                """)
    else:
        sql = text("""SELECT A.id
                FROM at_bats A
                JOIN games G
                   ON A.game_id = G.id
                WHERE A.game_id=:game_id
                AND A.b_team_id=G.h_team_id
                AND result IS NULL
                ORDER BY A.id DESC
                LIMIT 1
                """)
        
    result = db.session.execute(sql, {"game_id":game_id}).fetchone()
    if result is not None:
        return result[0]
    else:
        return None
    
def last_ab_id(game_id):
    """Return the id of the latest at bat for the home team."""
    inning = games.current_inning(game_id)
    if inning % 2 == 1:
        sql = text("""SELECT A.id
                FROM at_bats A
                JOIN games G
                ON A.b_team_id = G.a_team_id
                AND G.id=:game_id
                ORDER BY A.id DESC
                LIMIT 1
                """)
    else:
        sql = text("""SELECT A.id
                FROM at_bats A
                JOIN games G
                ON A.b_team_id = G.h_team_id
                AND G.id=:game_id
                ORDER BY A.id DESC
                LIMIT 1
                """)
    return db.session.execute(sql, {"game_id":game_id}).fetchone()[0]

def current_batter(ab_id):
    """Return the id of the current batter based on the at bat id."""
    sql = text("""SELECT batter_id
               FROM at_bats
               WHERE id=:ab_id
               """)
    return db.session.execute(sql, {"ab_id":ab_id}).fetchone()[0]

def handle_pitch(result, ab_id, game_id, runners: list):
    """Update the current at bat in the at_bats table based on the pitch result.
       Call functions to add runners, outs, or runs as needed. Call the function
       to finish the game if the home team obtains a lead in the final inning."""
    outs = 0
    runs = 0
    base_hits = ["Single", "Double", "Triple", "Home Run", "Single (out)", "Double (out)", "Triple (out)"]
    
    try:
        if result == "Strike (looking)":
            if strikes(ab_id) == 2:
                sql = text(ab_helpers.strike_looking(True))
                outs += 1
            else:
                sql = text(ab_helpers.strike_looking())

        elif result == "Strike (swinging)":
            if strikes(ab_id) == 2:
                sql = text(ab_helpers.strike_swinging(True))
                outs += 1
            else:
                sql = text(ab_helpers.strike_swinging())

        elif result == "Foul":
            if strikes(ab_id) == 2:
                sql = text(ab_helpers.foul(True))
            else:
                sql = text(ab_helpers.foul())

        elif result == "Ball" or result == "Intentional Walk":
            if balls(ab_id) == 3 or result == "Intentional Walk":
                sql, result, prev_runs = ab_helpers.ball(result, runners, ab_id, game_id, True)
            else:
                sql, result, prev_runs = ab_helpers.ball(result, runners, ab_id, game_id, False)

        elif result in base_hits:
            sql, runners, prev_runs, runs, outs = ab_helpers.base_hit(result, ab_id, game_id, runners, outs)

        elif result == "Fielder's choice":
            sql, prev_runs = ab_helpers.fielders_choice(ab_id, game_id, runners)

        elif result == "Sac fly" or result == "Sac bunt":
            sql, outs, prev_runs = ab_helpers.sac(game_id, runners, outs)

        else:
            sql, outs, prev_runs = ab_helpers.out(game_id, runners, outs)
        
        for runner in runners:
            if runner[1] == 0:
                outs += 1
                result += " +o"
            if runner[1] == 4:
                runs += 1
        
        if runs > 0:
            rbi(ab_id, runs)
            games.add_runs(game_id, runs, ab_id, prev_runs)

        if outs > 0:
            for i in range(outs):
                games.add_out(game_id)
        
        db.session.execute(sql, {"result":result, "ab_id":ab_id})
        db.session.commit()
        if games.current_inning(game_id) >= games.total_innings(game_id)*2 and games.runs_home(game_id) > games.runs_away(game_id):
            games.finish_game(game_id)
    except:
        return False
    return True

def strikes(ab_id):
    """Return the amount of strikes in the given at bat."""
    sql = text("""SELECT strikes
               FROM at_bats
               WHERE id=:ab_id
               """)
    return db.session.execute(sql, {"ab_id":ab_id}).fetchone()[0]

def balls(ab_id):
    """Return the amount of balls in the given at bat."""
    sql = text("""SELECT balls
               FROM at_bats
               WHERE id=:ab_id
               """)
    return db.session.execute(sql, {"ab_id":ab_id}).fetchone()[0]

def rbi(ab_id, rbi):
    """Add an rbi (run brought in) to an at bat."""
    try:
        sql = text("""UPDATE at_bats
                   SET rbi= rbi + :rbi
                   WHERE id=:ab_id
                   """)
        db.session.execute(sql, {"rbi":rbi, "ab_id":ab_id})
        db.session.commit()
    except:
        return False
    return True

def get_rbi(ab_id):
    """Return the amount of rbi from an at bat."""
    sql = text("""SELECT rbi
                    FROM at_bats
                    WHERE id = :ab_id
               """)
    return db.session.execute(sql, {"ab_id":ab_id}).fetchone()[0]