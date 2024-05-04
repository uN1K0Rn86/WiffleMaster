from sqlalchemy.sql import text
from db import db
import games
import at_bats

def strike_looking(two=False, out=""):
    """Handle the result for strike (looking)."""
    if two:
        out = ", result = 'Strikeout'"
    return f"""UPDATE at_bats
                SET strikes = strikes + 1{out}
                WHERE id=:ab_id
                """

def strike_swinging(two=False, out=""):
    """Handle the result for strike (swinging)."""
    if two:
        out = ", result = 'Strikeout (s)'"
    return f"""UPDATE at_bats
                SET strikes = strikes + 1, strswi = strswi + 1{out}
                WHERE id=:ab_id
                """

def foul(two=False):
    """Handle the result for a foul ball."""
    if two:
        result = "fouls = fouls + 1"
    else:
        result = "strikes = strikes + 1"
    return f"""UPDATE at_bats
                SET {result}
                WHERE id=:ab_id
                """

def ball(result, runners, ab_id, game_id, three=False):
    """Handle the result for a ball or intentional walk."""
    if three or result == "Intentional Walk":
        if result == "Intentional Walk":
            result = "IBB"
        else:
            result = "BB"
        if len(runners) > 0:
            if runners[0][1] == 1:
                runners[0][1] += 1
                if len(runners) > 1:
                    if runners[1][1] == 2:
                        runners[1][1] += 1
                        if len(runners) > 2:
                            runners[2][1] += 1

        games.add_runner(ab_id, game_id, 1)
        games.update_runners(game_id, runners)
        sql = text("""UPDATE at_bats
                SET balls = balls + 1, result = :result
                WHERE id=:ab_id
                """)
    
    else:
        sql = text("""UPDATE at_bats
                    SET balls = balls + 1
                    WHERE id=:ab_id
                    """)
        
    return sql

def base_hit(result, ab_id, game_id, runners):
    """Handle the result for a base hit"""
    runs = 0
    if result == "Home Run":
        runs = 1
        for runner in runners:
            runner[1] = 4
        base = 4
    elif result == "Triple":
        base = 3
    elif result == "Double":
        base = 2
    elif result == "Single":
        base = 1

    games.add_runner(ab_id, game_id, base)
    games.update_runners(game_id, runners)
    if runs == 1:
        at_bats.rbi(ab_id, 1)
        games.add_runs(game_id, 1)

    sql = text("""UPDATE at_bats
                SET result=:result, strikes = strikes + 1
                WHERE id=:ab_id
                """)
    
    return sql

def fielders_choice(ab_id, game_id, runners):
    """Handle the result for fielder's choice."""
    if len(runners) == 1 and runners[0][1] != 0:
        runners[0][1] = 0
    games.add_runner(ab_id, game_id, 1)
    games.update_runners(game_id, runners)
    sql = text("""UPDATE at_bats
                SET result=:result, strikes = strikes + 1
                WHERE id=:ab_id
                """)
    
    return sql

def sac(game_id, runners, outs):
    """Handle the result for a sac fly or sac bunt."""
    outs = outs
    games.update_runners(game_id, runners)
    sql = text("""UPDATE at_bats
                SET result=:result, strikes = strikes + 1
                WHERE id=:ab_id
                """)
    outs += 1

    return sql, outs

def out(game_id, runners, outs):
    """Handle the result for an out on a ball in play."""
    outs = outs
    games.update_runners(game_id, runners)
    sql = text("""UPDATE at_bats
                SET result=:result, strikes = strikes + 1
                WHERE id=:ab_id
                """)
    outs += 1

    return sql, outs