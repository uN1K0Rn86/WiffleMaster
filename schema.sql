CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);
CREATE TABLE players (id SERIAL PRIMARY KEY, name TEXT, bats TEXT, throws TEXT);
CREATE TABLE teams (id SERIAL PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE team_players (player_id INTEGER REFERENCES players, team_id INTEGER REFERENCES teams);
CREATE TABLE leagues (id SERIAL PRIMARY KEY, name TEXT);
CREATE TABLE league_teams (team_id INTEGER REFERENCES teams, league_id INTEGER REFERENCES leagues);
CREATE TABLE at_bats (id SERIAL PRIMARY KEY, batter_id INTEGER REFERENCES players, pitcher_id INTEGER REFERENCES players, 
strikes INTEGER, balls INTEGER, strswi INTEGER, result TEXT)