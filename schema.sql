CREATE TABLE users (id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT);

CREATE TABLE players (id SERIAL PRIMARY KEY,
                      name TEXT,
                      bats TEXT,
                      throws TEXT);

CREATE TABLE teams (id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE);

CREATE TABLE team_players (player_id INTEGER REFERENCES players,
                           team_id INTEGER REFERENCES teams);

CREATE TABLE leagues (id SERIAL PRIMARY KEY,
                      name TEXT UNIQUE);

CREATE TABLE league_teams (team_id INTEGER REFERENCES teams,
                           league_id INTEGER REFERENCES leagues);

CREATE TABLE games (id SERIAL PRIMARY KEY,
                    innings INTEGER,
                    a_team_id INTEGER REFERENCES teams,
                    h_team_id INTEGER REFERENCES teams,
                    a_team_runs INTEGER DEFAULT 0,
                    h_team_runs INTEGER DEFAULT 0,
                    league_id INTEGER,
                    in_progress BOOLEAN DEFAULT true,
                    inning INTEGER DEFAULT 1,
                    game_time TIMESTAMP,
                    outs INTEGER DEFAULT 0,
                    h_order INTEGER[],
                    a_order INTEGER[],
                    h_pitcher INTEGER REFERENCES players,
                    a_pitcher INTEGER REFERENCES players,
                    h_previous INTEGER DEFAULT -2,
                    a_previous INTEGER DEFAULT -2);

CREATE TABLE at_bats (id SERIAL PRIMARY KEY,
                      batter_id INTEGER REFERENCES players,
                      pitcher_id INTEGER REFERENCES players,
                      strikes INTEGER DEFAULT 0,
                      balls INTEGER DEFAULT 0,
                      strswi INTEGER DEFAULT 0,
                      fouls INTEGER DEFAULT 0,
                      result TEXT,
                      outs INTEGER DEFAULT 0,
                      inning INTEGER DEFAULT 1,
                      rbi INTEGER DEFAULT 0,
                      p_team_id INTEGER REFERENCES teams,
                      b_team_id INTEGER REFERENCES teams,
                      game_id INTEGER REFERENCES games);

CREATE TABLE runners (id SERIAL PRIMARY KEY,
                      runner_id INTEGER REFERENCES players,
                      pitcher_id INTEGER REFERENCES players,
                      game_id INTEGER REFERENCES games,
                      status INTEGER);