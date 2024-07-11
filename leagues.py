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
                            OR (G.a_team_runs > G.h_team_runs AND G.a_team_id = T.id) THEN 1 ELSE 0 END) :: FLOAT /
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

def batting_average(league_id, player_id):
    """Return the batting average for a player in a given league."""
    sql = text("""SELECT
                    COALESCE(
                        CASE 
                            WHEN (COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) - 
                                COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                                COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0)) = 0 
                            THEN 0
                            ELSE SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END) :: FLOAT /
                                (COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) -
                                COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                                COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0))
                        END, 0) AS avg
                    FROM players P
                    LEFT JOIN at_bats A ON A.batter_id = P.id
                    AND P.id = :player_id
                    JOIN games G ON A.game_id = G.id
                    JOIN leagues L ON G.league_id = L.id
                    AND L.id = :league_id
               """)
    return db.session.execute(sql, {"player_id":player_id, "league_id":league_id}).fetchone()[0]

def batting_leaders(league_id, amount, offset, sort, asc=False):
    """Return batting statistics for players in this league."""
    direction = "ASC" if asc else "DESC"
    order_by = f"ORDER BY {sort} {direction}"
    sql = text(f"""SELECT
                    P.id AS id,
                    P.name AS name,
                    COUNT(DISTINCT A.game_id) AS g,
                    COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) AS pa,
                    COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) AS walks,
                    COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) AS hits,
                    COALESCE(SUM(CASE WHEN A.result IN ('Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) AS xbh,
                    COALESCE(SUM(CASE WHEN A.result = 'Home Run' THEN 1 ELSE 0 END), 0) AS hr,
                    COALESCE(SUM(CASE WHEN A.result = 'Triple' THEN 1 ELSE 0 END), 0) AS triples,
                    COALESCE(SUM(CASE WHEN A.result = 'Double' THEN 1 ELSE 0 END), 0) AS doubles,
                    COALESCE(SUM(CASE WHEN A.result = 'Single' THEN 1 ELSE 0 END), 0) AS singles,
                    COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0) AS sacs,
                    COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                        COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0) AS ab,
                    COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END) :: FLOAT /
                        (COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                        COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0)), 0) AS avg,
                    (COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) :: FLOAT +
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0)) / 
                        COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) AS obp,
                    ((COALESCE(SUM(CASE WHEN A.result = 'Single' THEN 1 ELSE 0 END), 0) +
                        2 * COALESCE(SUM(CASE WHEN A.result = 'Double' THEN 1 ELSE 0 END), 0) +
                        3 * COALESCE(SUM(CASE WHEN A.result = 'Triple' THEN 1 ELSE 0 END), 0) +
                        4 * COALESCE(SUM(CASE WHEN A.result = 'Home Run' THEN 1 ELSE 0 END))) :: FLOAT /
                        (COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                        COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0))) AS slg,
                    SUM(rbi) AS rbi,
                    ((COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0) :: FLOAT +
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0)) / 
                        COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0)) +
                        (((COALESCE(SUM(CASE WHEN A.result = 'Single' THEN 1 ELSE 0 END), 0) +
                        2 * COALESCE(SUM(CASE WHEN A.result = 'Double' THEN 1 ELSE 0 END), 0) +
                        3 * COALESCE(SUM(CASE WHEN A.result = 'Triple' THEN 1 ELSE 0 END), 0) +
                        4 * COALESCE(SUM(CASE WHEN A.result = 'Home Run' THEN 1 ELSE 0 END))) :: FLOAT /
                        (COALESCE(SUM(CASE WHEN A.result IS NOT NULL THEN 1 ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN A.result IN ('BB', 'IBB') THEN 1 ELSE 0 END), 0) - 
                        COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0)))) AS ops
                FROM players P
                LEFT JOIN at_bats A ON A.batter_id = P.id
                JOIN games G ON A.game_id = G.id
                JOIN leagues L ON G.league_id = L.id
                AND L.id = :league_id
                GROUP BY P.id
                {order_by}
                LIMIT :amount
                OFFSET :offset
               """)
    return db.session.execute(sql, {"league_id":league_id, "amount":amount, "offset":offset}).fetchall()

def pitching_leaders(league_id, amount, offset, sort, asc=False):
    """Return pitching statistics for players in this league."""
    direction = "ASC" if asc else "DESC"
    order_by = f"ORDER BY {sort} {direction}"
    outs = """(COALESCE(SUM(CASE WHEN A.result LIKE '%out%' THEN 1 ELSE 0 END), 0) +
              COALESCE(SUM(CASE WHEN A.result LIKE '%+o%' THEN 1 ELSE 0 END), 0) +
              COALESCE(SUM(CASE WHEN A.result IN ('Sac fly', 'Sac bunt') THEN 1 ELSE 0 END), 0))"""
    k = "COALESCE(SUM(CASE WHEN A.result IN ('Strikeout', 'Strikeout (s)') THEN 1 ELSE 0 END), 0)"
    bb = "COALESCE(SUM(CASE WHEN A.result in ('BB', 'IBB') THEN 1 ELSE 0 END), 0)"
    hits = "COALESCE(SUM(CASE WHEN A.result IN ('Single', 'Double', 'Triple', 'Home Run') THEN 1 ELSE 0 END), 0)"
    r = "COALESCE(SUM(rbi), 0)"
    sql = text(f"""SELECT
                    P.id AS id,
                    P.name AS name,
                    COUNT(DISTINCT A.game_id) AS g,
                    {outs} AS outs,
                    {k} AS k,
                    CASE WHEN {outs} = 0 THEN 0 ELSE ({k}) ::FLOAT / (({outs}) ::FLOAT / 27) END AS k9,
                    {bb} AS bb,
                    CASE WHEN {outs} = 0 THEN 0 ELSE ({bb}) ::FLOAT / (({outs}) ::FLOAT / 27) END AS bb9,
                    {hits} AS hits,
                    CASE WHEN {outs} = 0 THEN 0 ELSE ({hits}) ::FLOAT / (({hits}) + ({outs}) ::FLOAT) END AS baa,
                    {r} AS r,
                    CASE WHEN {outs} = 0 THEN 0 ELSE ({r}) ::FLOAT / (({outs}) ::FLOAT / 27) END AS era
                FROM players P
                LEFT JOIN at_bats A ON A.pitcher_id = P.id
                JOIN games G ON A.game_id = G.id
                JOIN leagues L ON G.league_id = L.id
                AND L.id = :league_id
                GROUP BY P.id
                {order_by}
                LIMIT :amount
                OFFSET :offset
               """)
    return db.session.execute(sql, {"league_id":league_id, "amount":amount, "offset":offset}).fetchall()