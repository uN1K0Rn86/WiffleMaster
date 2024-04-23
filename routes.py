from app import app
from flask import render_template, request, redirect, url_for, session
import users
import players
import teams
import leagues
import games
import at_bats

@app.route("/")
def index():
    """Return the template for index.html."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Return the template for login.html.
    Process the user input from login.html.
    Call the user login function.
    If login fails, return the error template.
    """
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return render_template("login.html", error_message="Please do not leave any blank fields.")
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("login.html", error_message="Wrong username or password")
        
@app.route("/register", methods=["GET", "POST"])
def register():
    """Return the template for register.html.
    Process the user input from register.html.
    Call the registration function.
    If registration fails, return the error template."""
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not username or not password1 or not password2:
            return render_template("register.html", error_message="Please do not leave any blank fields.")
        if password1 != password2:
            return render_template("register.html", error_message="Passwords do not match.")
        if users.register(username, password1):
            return redirect("/")
        else:
            return render_template("register.html", error_message="That username is already in use.")
        
@app.route("/logout")
def logout():
    """Call the logout function.
    Redirect to the home page.
    """
    users.logout()
    return redirect("/")

@app.route("/rules")
def rules():
    """Return the template for rules.html."""
    return render_template("rules.html")

@app.route("/players", methods=["GET", "POST"])
def go_players():
    """Return the template for players.html.
    Process user input and add player to database.
    """
    player_list = players.display_players()
    if request.method == "GET":
        return render_template("players.html", player_list=player_list)
    if request.method == "POST":
        name = request.form["name"]
        if "bats" in request.form:
            bats = request.form["bats"]
        else:
            bats = None

        if "throws" in request.form:
            throws = request.form["throws"]
        else:
            throws = None
    
        if not name:
            return render_template("players.html", player_list=player_list, bats=bats, throws=throws,
                                    error_message="A player must have a name.")
        if not bats or not throws:
            return render_template("players.html", player_list=player_list,
                                   error_message="Please select values for batting and throwing handedness.",
                                   name=name, throws=throws, bats=bats)
        
        if players.add_player(name, bats, throws):
            return redirect("/players")
        else:
            return render_template("players.html", player_list=player_list,
                                   error_message="Could not add player. Did you provide all the information?")
        
@app.route("/players/<int:id>")
def player_page(id):
    player = players.display_player(id)
    return render_template("player.html", player=player)

@app.route("/teams", methods=["GET", "POST"])
def go_teams():
    """Return the template for teams.html.
    Process user input and add team to database.
    """
    team_list = teams.show_teams()
    if request.method == "GET":
        return render_template("teams.html", team_list=team_list)
    if request.method == "POST":
        name = request.form["name"]
        if teams.add_team(name):
            return redirect("/teams")
        else:
            return render_template("teams.html", error_message="A team with that name already exists.",
                                   team_list=team_list)
        
@app.route("/teams/<int:id>", methods=["GET", "POST"])
def team_page(id):
    if request.method == "GET":
        team = teams.show_team(id)
        team_players_ids = [player[0] for player in teams.list_players(id)]
        team_players = [players.batting_stats(player) for player in team_players_ids]
        teamless = players.list_teamless()
        others = teams.list_players_other(id)
        record = teams.record(id)
        return render_template("team.html", team=team, team_players=team_players, teamless=teamless, others=others,
                               record=record)
    
    if request.method == "POST":
        team_id = id
        direct = f"/teams/{id}"
        if "players" in request.form:
            player_id = request.form["players"]
            if teams.add_player(player_id, team_id):
                return redirect(direct)
        elif "move" in request.form:
            move_p_id = request.form["move"]
            if teams.move_player(move_p_id, team_id):
                return redirect(direct)
        
@app.route("/leagues", methods=["GET", "POST"])
def go_leagues():
    """Return the template for leagues.html.
    Process user input and add a league to database
    """
    league_list = leagues.show_leagues()
    if request.method == "GET":
        return render_template("leagues.html", league_list=league_list)
    if request.method == "POST":
        name = request.form["name"]
        if not name:
            return render_template("leagues.html", league_list=league_list,
                                   error_message="Please give a name for the league.")
        if leagues.add_league(name):
            return redirect("/leagues")
        else:
            return render_template("leagues.html", league_list=league_list,
                                   error_message="A league with that name already exists. Please select a different name.")
        
@app.route("/leagues/<int:id>", methods=["GET", "POST"])
def league_page(id):
    """Return the template for the league in question."""
    if request.method == "GET":
        league = leagues.show_league(id)
        league_teams = leagues.show_teams(id)
        others = leagues.show_other_teams(id)
        table = leagues.league_table(id)
        first_wins = table[0].wins
        first_losses = table[0].losses
        return render_template("league.html", league=league, league_teams=league_teams, others=others, table=table,
                               first_wins=first_wins, first_losses=first_losses)
    if request.method == "POST":
        team = request.form["team"]
        direct = f"/leagues/{id}"
        if leagues.add_team(team, id):
            return redirect(direct)
        
@app.route("/games", methods=["GET", "POST"])
def go_games():
    """Return the template for creating games."""
    all_teams = teams.show_teams()
    all_leagues = leagues.show_leagues()
    in_progress = games.games_in_progress()
    latest = games.latest(5)

    if request.method == "GET":
        return render_template("games.html", all_teams=all_teams, all_leagues=all_leagues, in_progress=in_progress,
                               latest=latest)
    
    if request.method == "POST":
        a_team_id = int(request.form["a_team"])
        h_team_id = int(request.form["h_team"])
        league_id = int(request.form["league"])
        innings = int(request.form["innings"])

        if a_team_id == h_team_id:
            return render_template("games.html", error_message="Please choose two different teams.",
                                   all_teams=all_teams, all_leagues=all_leagues, in_progress=in_progress,
                                   latest=latest, a_team_id=a_team_id, h_team_id=h_team_id, league_id=league_id,
                                   innings=innings)
        
        game_id = games.new_game(innings, a_team_id, h_team_id, league_id)
        return redirect(url_for("go_order", game_id=game_id))

@app.route("/games/<int:id>", methods=["GET", "POST"])
def game_page(id):
    """Return the page for the game in question and handle game events."""
    h_team = games.home_team(id)
    a_team = games.away_team(id)

    h_order = games.get_h_order(id)
    h_order = [players.player_name(player) for player in h_order]
    h_pitcher = players.player_name(games.get_h_pitcher(id))

    a_order = games.get_a_order(id)
    a_order = [players.player_name(player) for player in a_order]
    a_pitcher = players.player_name(games.get_a_pitcher(id))

    inning = games.current_inning(id)
    total_innings = games.total_innings(id)
    runs_inning = [games.runs_inning(id, i) for i in range(1, inning + 1)]

    runs_home = games.runs_home(id)
    runs_away = games.runs_away(id)
    hits_home = games.hits_home(id)
    hits_away = games.hits_away(id)

    pitch_results = at_bats.pitch_results()
    runners = games.get_runners(id)
    outs = games.get_outs(id)
    in_progress = games.in_progress(id)
    
    if request.method == "GET":
        # This if block is for the top of the inning; the away team is batting and the home team is pitching.
        if inning % 2 == 1:
            # This makes sure the correct batter is retrieved.
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    last = games.get_a_previous(id)
                    if last >= len(a_order) - 2:
                        games.set_a_previous(id, -1)
                    else:
                        games.set_a_previous(id, last+1)

            previous = games.get_a_previous(id)
            batter = games.batter_up(a_order, previous) # The current batter.
            batter_stats = games.batting_stats(id, batter[0])
            on_deck = games.batter_up(a_order, previous+1) # The next batter.
            on_deck_stats = games.batting_stats(id, on_deck[0])
            pitcher = h_pitcher # The current pitcher.
            p_players = teams.list_players(h_team[0]) # List of players available for a pitcher change.

            # This creates an at bat.
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    at_bats.create_at_bat(id, batter[0], pitcher[0], h_team[0], a_team[0])
            ab_id = at_bats.current_ab_id(id)
            if in_progress:
                count = (at_bats.balls(ab_id), at_bats.strikes(ab_id))
            else:
                count = (0, 0)
            pitch_count = games.pitch_count(id, h_pitcher[0])

        # This block is for the bottom of the inning i.e. the home team is batting and the away team is pitching.  
        else:
            # This makes sure the correct batter is retrieved.
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    last = games.get_h_previous(id)
                    if last >= len(h_order) - 2:
                        games.set_h_previous(id, -1)
                    else:
                        games.set_h_previous(id, last+1)

            previous = games.get_h_previous(id)
            batter = games.batter_up(h_order, previous) # The current batter.
            batter_stats = games.batting_stats(id, batter[0])
            on_deck = games.batter_up(h_order, previous+1) # The next batter.
            on_deck_stats = games.batting_stats(id, on_deck[0])
            pitcher = a_pitcher # The current pitcher.
            p_players = teams.list_players(a_team[0]) # List of players available for a pitcher change.

            # This creates an at bat.
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    at_bats.create_at_bat(id, batter[0], pitcher[0], a_team[0], h_team[0])
            ab_id = at_bats.current_ab_id(id)
            if in_progress:
                count = (at_bats.balls(ab_id), at_bats.strikes(ab_id))
            else:
                count = (0, 0)
            pitch_count = games.pitch_count(id, a_pitcher.id)

        return render_template("game.html", id=id, pitcher=pitcher, runs_inning=runs_inning,
                               h_team=h_team, a_team=a_team, total_innings=total_innings,
                               inning=inning, batter=batter, on_deck=on_deck, runs_home=runs_home,
                               runs_away=runs_away, p_players=p_players, batter_stats=batter_stats,
                               on_deck_stats=on_deck_stats, pitch_results=pitch_results,
                               runners=runners, outs=outs, count=count, pitch_count=pitch_count,
                               in_progress=in_progress, hits_home=hits_home, hits_away=hits_away)
    
    if request.method == "POST":
        # This handles the form if the pitcher is changed.
        if "new_pitcher" in request.form:
            new_pitcher = request.form["new_pitcher"]
            if inning % 2 == 1:
                if games.change_h_pitcher(id, new_pitcher):
                    return redirect(url_for("game_page", id=id))
                else:
                    return render_template("error.html", message="Could not change pitcher")
            else:
                if games.change_a_pitcher(id, new_pitcher):
                    return redirect(url_for("game_page", id=id))
                else:
                    return render_template("error.html", message="Could not change pitcher")
                
        # This handles the form if a pitch was logged.
        elif "pitch" in request.form:
            result = request.form["pitch"]
            runners = []
            # Check if there are any runners and add them to the list of runners.
            if "runner1" in request.form:
                runner1 = games.parse_option(request.form["runner1"])
                runners.append(runner1)
            if "runner2" in request.form:
                runner2 = games.parse_option(request.form["runner2"])
                runners.append(runner2)
            if "runner3" in request.form:
                runner3 = games.parse_option(request.form["runner3"])
                runners.append(runner3)
            ab_id = at_bats.current_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)
        return redirect(url_for("game_page", id=id))

@app.route("/games/order/<game_id>", methods=["GET", "POST"])
def go_order(game_id):
    """Return the template for setting the batting order."""

    h_team = games.home_team(game_id) # The home team.
    a_team = games.away_team(game_id) # The away team.

    if request.method == "GET":
        h_players = teams.list_players(h_team[0]) # Players on the home team.
        a_players = teams.list_players(a_team[0]) # Players on the away team.
        return render_template("order.html", h_players=h_players, a_players=a_players, game_id=game_id)
    
    if request.method == "POST":
        h_players = teams.list_players(h_team[0]) # Players on the home team.
        a_players = teams.list_players(a_team[0]) # Players on the away team.

        # Retrieve the batting order for the home team.
        h_order = request.form.getlist("h_order")
        
        h_pitcher = request.form["h_pitcher"] # The starting pitcher for the home team.
        a_pitcher = request.form["a_pitcher"] # The starting pitcher for the away team.

        # Retrieve the batting order for the away team.
        a_order = request.form.getlist("a_order")

        # Remove "None" responses from the order forms for checking purposes and turn values into integers.
        h_order = [int(player_id) for player_id in h_order if player_id != "None"]
        a_order = [int(player_id) for player_id in a_order if player_id != "None"]

        # Make sure that a batter is not in the order twice.
        if len(a_order) != len(set(a_order)) or len(h_order) != len(set(h_order)):
            return render_template("order.html", h_players=h_players, a_players=a_players, game_id=game_id,
                                   error_message="Please select only unique batters", a_order=a_order,
                                   h_order=h_order, h_pitcher=h_pitcher, a_pitcher=a_pitcher)

        # Make sure that there are at least two batters on each team.
        if len(a_order) < 2 or len(h_order) < 2:
            return render_template("order.html", h_players=h_players, a_players=a_players, game_id=game_id,
                                   error_message="Please select at least 2 batters for both teams.", a_order=a_order,
                                   h_order=h_order, h_pitcher=h_pitcher, a_pitcher=a_pitcher)

        if games.set_order(game_id, h_order, a_order, h_pitcher, a_pitcher):
            return redirect(url_for("game_page", id=game_id))