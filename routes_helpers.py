from app import app
import games
import players
import at_bats
import teams

def h_team(game_id):
    """Return a dictionary of information for the home team."""
    h = {}
    h["id"] = games.home_team(game_id)
    h["order"] = [players.player_name(player) for player in games.get_h_order(game_id)]
    h["pitcher"] = players.player_name(games.get_h_pitcher(game_id))
    h["runs"] = games.runs_home(game_id)
    h["hits"] = games.hits_home(game_id)

    return h


def a_team(game_id):
    """Return a dictionary of information for the away team."""
    a = {}
    a["id"] = games.away_team(game_id)
    a["order"] = [players.player_name(player) for player in games.get_a_order(game_id)]
    a["pitcher"] = players.player_name(games.get_a_pitcher(game_id))
    a["runs"] = games.runs_away(game_id)
    a["hits"] = games.hits_away(game_id)

    return a

def update_current_players(game_id, h_team, a_team):
    """Update the previous batter."""
    inning = games.current_inning(game_id)
    in_progress = games.in_progress(game_id)
    last = games.get_previous(game_id)
    current = {}

    if inning % 2 == 1:
        if in_progress:
            if at_bats.current_ab_id(game_id) is None:
                if last >= len(a_team["order"]) - 2:
                    games.set_previous(game_id, -1)
                else:
                    games.set_previous(game_id, last+1)

        previous = games.get_previous(game_id)
        current["batter"] = games.batter_up(a_team["order"], previous) # The current batter.
        current["on_deck"] = games.batter_up(a_team["order"], previous+1) # The next batter.
        current["pitcher"] = h_team["pitcher"] # The current pitcher.
        current["p_players"] = teams.list_players(h_team["id"][0]) # List of players available for a pitching change.
        current["batting_team"] = a_team["id"][0]
        current["pitching team"] = h_team["id"][0]
    
    else:
        if in_progress:
            if at_bats.current_ab_id(game_id) is None:
                if last >= len(h_team["order"]) - 2:
                    games.set_previous(game_id, -1)
                else:
                    games.set_previous(game_id, last+1)

        previous = games.get_previous(game_id)
        current["batter"] = games.batter_up(h_team["order"], previous) # The current batter.
        current["on_deck"] = games.batter_up(h_team["order"], previous+1) # The next batter.
        current["pitcher"] = a_team["pitcher"]# The current pitcher.
        current["p_players"] = teams.list_players(a_team["id"][0]) # List of players available for a pitching change.
        current["batting_team"] = h_team["id"][0]
        current["pitching team"] = a_team["id"][0]

    current["batter_stats"] = games.batting_stats(game_id, current["batter"][0])
    current["on_deck_stats"] = games.batting_stats(game_id, current["on_deck"][0])

    # This creates an at bat.
    if in_progress:
        if at_bats.current_ab_id(game_id) is None:
            at_bats.create_at_bat(game_id, current["batter"][0], current["pitcher"][0], current["batting_team"], current["pitching team"])
    ab_id = at_bats.current_ab_id(game_id)
    if in_progress:
        current["count"] = (at_bats.balls(ab_id), at_bats.strikes(ab_id))
    else:
        current["count"] = (0, 0)
    current["pitch_count"] = games.pitch_count(game_id, current["pitcher"][0])

    return current