from sqlalchemy.sql import text
from db import db
import games

def pitch_results():
    """Return a list of possible results for any pitch."""
    return ["Strike (looking)", "Strike (swinging)", "Foul", "Ball", "Intentional Walk", "Single", "Double", "Triple", "Home Run",
            "Groundout", "Flyout", "Lineout"]

def create_at_bat(game_id, batter_id, pitcher_id, p_team_id, b_team_id):
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
    sql = text("""SELECT id
               FROM at_bats
               WHERE game_id=:game_id
               AND result IS NULL
               AND id >= (SELECT MAX(id)
                        FROM at_bats
                        WHERE game_id = :game_id)
               ORDER BY id DESC
               LIMIT 1
               """)
    result = db.session.execute(sql, {"game_id":game_id}).fetchone()
    if result is not None:
        return result[0]
    else:
        return None

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
    for runner in runners:
        if runner[1] == 4:
            runs += 1
        if runner[1] == 0:
            outs += 1
    try:
        if result == "Strike (looking)":
            if strikes(ab_id) == 2:
                sql = text("""UPDATE at_bats
                       SET strikes = strikes + 1, result = 'Strikeout'
                       WHERE id=:ab_id
                       """)
                outs += 1
            else:
                sql = text("""UPDATE at_bats
                       SET strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Strike (swinging)":
            if strikes(ab_id) == 2:
                sql = text("""UPDATE at_bats
                       SET strikes = strikes + 1, strswi = strswi + 1, result = 'Strikeout (s)'
                       WHERE id=:ab_id
                       """)
                outs += 1
            else:
                sql = text("""UPDATE at_bats
                       SET strikes = strikes + 1, strswi = strswi + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Foul":
            if strikes(ab_id) == 2:
                sql = text("""UPDATE at_bats
                           SET fouls = fouls + 1
                           WHERE id=:ab_id
                           """)
            else:
                sql = text("""UPDATE at_bats
                           SET strikes = strikes + 1
                           WHERE id=:ab_id
                           """)
        elif result == "Ball":
            if balls(ab_id) == 3:
                if len(runners) > 0:
                    if runners[0][1] == 1:
                        runners[0][1] += 1
                        if len(runners) > 1:
                            if runners[1][1] == 2:
                                runners[1][1] += 1
                                if len(runners) > 2:
                                    if runners[2][1] == 3:
                                        runners[2][1] += 1
                                        runs += 1
                games.add_runner(ab_id, game_id, 1)
                games.update_runners(game_id, runners)
                sql = text("""UPDATE at_bats
                       SET balls = balls + 1, result = 'BB'
                       WHERE id=:ab_id
                       """)
            else:
                sql = text("""UPDATE at_bats
                       SET balls = balls + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Intentional Walk":
            if len(runners) > 0:
                    if runners[0][1] == 1:
                        runners[0][1] += 1
                        if len(runners) > 1:
                            if runners[1][1] == 2:
                                runners[1][1] += 1
                                if len(runners) > 2:
                                    if runners[2][1] == 3:
                                        runners[2][1] += 1
                                        runs += 1
            games.add_runner(ab_id, game_id, 1)
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                    SET result = 'IBB'
                    WHERE id=:ab_id
                    """)
        elif result == "Single":
            games.add_runner(ab_id, game_id, 1)
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                       SET result=:result, strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Double":
            games.add_runner(ab_id, game_id, 2)
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                       SET result=:result, strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Triple":
            games.add_runner(ab_id, game_id, 3)
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                       SET result=:result, strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
        elif result == "Home Run":
            games.add_runner(ab_id, game_id, 4)
            runs = 1
            for runner in runners:
                runner[1] = 4
                runs += 1
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                       SET result=:result, strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
        else:
            games.update_runners(game_id, runners)
            sql = text("""UPDATE at_bats
                       SET result=:result, strikes = strikes + 1
                       WHERE id=:ab_id
                       """)
            outs += 1
            
        if runs > 0:
            rbi(ab_id, runs)
            games.add_runs(game_id, runs)

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
                   SET rbi=:rbi
                   WHERE id=:ab_id
                   """)
        db.session.execute(sql, {"rbi":rbi, "ab_id":ab_id})
        db.session.commit()
    except:
        return False
    return True