from sqlalchemy.sql import text
from db import db
import games
import at_bats

def strike_looking(two=False, out=""):
    if two:
        out = ", result = 'Strikeout'"
    return f"""UPDATE at_bats
                SET strikes = strikes + 1{out}
                WHERE id=:ab_id
                """

def strike_swinging(two=False, out=""):
    if two:
        out = ", result = 'Strikeout (s)'"
    return f"""UPDATE at_bats
                SET strikes = strikes + 1, strswi = strswi + 1{out}
                WHERE id=:ab_id
                """

def foul(two=False):
    if two:
        result = "fouls = fouls + 1"
    else:
        result = "strikes = strikes + 1"
    return f"""UPDATE at_bats
                SET {result}
                WHERE id=:ab_id
                """

def ball(result, runners, runs, ab_id, game_id, three=False):
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
                            runs += 1
        games.add_runner(ab_id, game_id, 1)
        games.update_runners(game_id, runners)
        sql = text(f"""UPDATE at_bats
                SET balls = balls + 1, result = '{result}'
                WHERE id=:ab_id
                """)
    
    else:
        sql = text("""UPDATE at_bats
                    SET balls = balls + 1
                    WHERE id=:ab_id
                    """)
        
    return sql, runs