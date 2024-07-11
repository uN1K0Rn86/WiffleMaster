from flask import render_template, request, redirect, url_for, session, abort
from app import app
import users
import players
import teams
import leagues
import games
import at_bats
import routes_helpers

@app.before_request
def csrf_protect():
    excluded = ["/login", "/register"]
    if request.method == "POST" and request.path not in excluded:
        csrf_token = session["csrf_token"]
        if not csrf_token or csrf_token != request.form["csrf_token"]:
            abort(403)

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
        if name == "":
            return render_template("teams.html", error_message="Please provide a name for the team.",
                                   team_list=team_list)
        if teams.add_team(name):
            return redirect("/teams")
        else:
            return render_template("teams.html", error_message="A team with that name already exists.",
                                   team_list=team_list)
        
@app.route("/teams/<int:id>", methods=["GET", "POST"])
def team_page(id):
    team = teams.show_team(id)
    team_players_ids = [player[0] for player in teams.list_players(id)]
    team_players = [players.batting_stats(player) for player in team_players_ids]
    teamless = players.list_teamless()
    others = teams.list_players_other(id)
    record = teams.record(id)
    if request.method == "GET":
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
            
        else:
            error_message = "Please choose a player to add. If there are no players, create one from the players page."
            return render_template("team.html", team=team, team_players=team_players, teamless=teamless, others=others,
                            record=record, error_message=error_message)
        
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
    league = leagues.show_league(id)
    league_teams = leagues.show_teams(id)
    others = leagues.show_other_teams(id)
    table = leagues.league_table(id)

    if table:
        first_wins = table[0].wins
        first_losses = table[0].losses
    else:
        first_wins = first_losses = 0
        
    batting_values = players.batting_values()
    pitching_values = players.pitching_values()

    if request.method == "GET":
        batting_size = 10
        pitching_size = 10
        batting_leaders = leagues.batting_leaders(id, batting_size, 0, "avg", False)
        pitching_leaders = leagues.pitching_leaders(id, 10, 0, "era", False)
        return render_template("league.html", league=league, league_teams=league_teams, others=others, table=table,
                               first_wins=first_wins, first_losses=first_losses, batting_leaders=batting_leaders,
                               batting_size=batting_size, len_batting=len(batting_leaders), batting_values=batting_values,
                               pitching_leaders=pitching_leaders, pitching_values=pitching_values,
                               pitching_size=pitching_size, len_pitching=len(pitching_leaders))
    
    if request.method == "POST":
        if "team" in request.form:
            team = request.form["team"]
            direct = f"/leagues/{id}"
            if leagues.add_team(team, id):
                return redirect(direct)

        if "sort" in request.form:
            sort = request.form["sort"]
            asc = False if request.form["order"] == "desc" else True
            batting_size = int(request.form["batting_size"])
            page = request.form["page"]
            offset = (int(page) - 1) * batting_size
            batting_leaders = leagues.batting_leaders(id, batting_size, offset, sort, asc)
            pitching_size = 10
            pitching_leaders = leagues.pitching_leaders(id, pitching_size, 0, "era", False)
            return render_template("league.html", league=league, league_teams=league_teams, others=others, table=table,
                               first_wins=first_wins, first_losses=first_losses, batting_leaders=batting_leaders,
                               batting_size=batting_size, len_batting=len(batting_leaders), batting_values=batting_values,
                               sort=sort, page=page, pitching_leaders=pitching_leaders, pitching_values=pitching_values,
                               pitching_size=pitching_size, len_pitching=len(pitching_leaders))
        
        if "sort2" in request.form:
            sort = request.form["sort2"]
            asc = False if request.form["order2"] == "desc" else True
            batting_size = 10
            page = request.form["page2"]
            pitching_size = int(request.form["pitching_size"])
            offset = (int(page) - 1) * pitching_size
            batting_leaders = leagues.batting_leaders(id, batting_size, 0, "avg", False)
            pitching_leaders = leagues.pitching_leaders(id, pitching_size, offset, sort, asc)
            return render_template("league.html", league=league, league_teams=league_teams, others=others, table=table,
                               first_wins=first_wins, first_losses=first_losses, batting_leaders=batting_leaders,
                               batting_size=batting_size, len_batting=len(batting_leaders), batting_values=batting_values,
                               sort=sort, page=page, pitching_leaders=pitching_leaders, pitching_values=pitching_values,
                               pitching_size=pitching_size, len_pitching=len(pitching_leaders))
        
        else:
            batting_size = 10
            batting_leaders = leagues.batting_leaders(id, batting_size, 0, "avg", False)
            pitching_size = 10
            pitching_leaders = leagues.pitching_leaders(id, pitching_size, 0, "era", False)
            error_message = "Please choose a team to add. If there are no teams available, create one from the Teams page."
            return render_template("league.html", league=league, league_teams=league_teams, others=others, table=table,
                                first_wins=first_wins, first_losses=first_losses, batting_leaders=batting_leaders,
                                batting_size=batting_size, len_batting=len(batting_leaders), batting_values=batting_values,
                                error_message=error_message, pitching_leaders=pitching_leaders, pitching_values=pitching_values,
                                pitching_size=pitching_size, len_pitching=len(pitching_leaders))
        
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
        max_runs = int(request.form["max_runs"])
        error_message = None

        if len(teams.list_players(a_team_id)) < 2:
            error_message = "The away team does not have enough players. Please make sure there are at least two players on every team."

        if len(teams.list_players(h_team_id)) < 2:
            error_message = "The home team does not have enough players. Please make sure there are at least two players on every team."

        if a_team_id == h_team_id:
            error_message = "Please choose two different teams."
        
        if error_message:
            return render_template("games.html", all_teams=all_teams, all_leagues=all_leagues, in_progress=in_progress,
                                   latest=latest, a_team_id=a_team_id, h_team_id=h_team_id, league_id=league_id, innings=innings,
                                   max_runs=max_runs, error_message=error_message)
        
        else:
            game_id = games.new_game(innings, a_team_id, h_team_id, league_id, max_runs)
            return redirect(url_for("go_order", game_id=game_id))

@app.route("/games/<int:id>", methods=["GET", "POST"])
def game_page(id):
    """Return the page for the game in question and handle game events."""
    h_team = routes_helpers.h_team(id)
    a_team = routes_helpers.a_team(id)
    current = routes_helpers.update_current_players(id, h_team, a_team)

    inning = games.current_inning(id)
    total_innings = games.total_innings(id)

    max_runs = games.get_max_runs_inning(id, inning)
    runs_inning = []
    for i in range(1, inning + 1):
        away, home = games.runs_before_inning(id, i)
        if i % 2 == 1:
            if home - away > max_runs:
                max_runs = home - away
        else:
            if away - home > max_runs:
                max_runs = away - home
        runs_inning.append(min(games.runs_inning(id, i), max_runs))

    runs_home = games.runs_home(id)
    runs_away = games.runs_away(id)
    hits_home = games.hits_home(id)
    hits_away = games.hits_away(id)
    box_away, box_home = games.box_scores(id)

    pitch_results = at_bats.pitch_results()
    runners = games.get_runners(id)
    outs = games.get_outs(id)
    in_progress = games.in_progress(id)
    
    if request.method == "GET":
        return render_template("game.html", id=id, pitcher=current["pitcher"], runs_inning=runs_inning,
                               h_team=h_team["id"], a_team=a_team["id"], total_innings=total_innings,
                               inning=inning, batter=current["batter"], on_deck=current["on_deck"], runs_home=runs_home,
                               runs_away=runs_away, p_players=current["p_players"], batter_stats=current["batter_stats"],
                               on_deck_stats=current["on_deck_stats"], pitch_results=pitch_results,
                               runners=runners, outs=outs, count=current["count"], pitch_count=current["pitch_count"],
                               in_progress=in_progress, hits_home=hits_home, hits_away=hits_away, box_away=box_away,
                               box_home=box_home, all_players=current["all_players"])
    
    if request.method == "POST":
        # This handles the form if the pitcher is changed.
        if "new_pitcher" in request.form:
            new_pitcher = request.form["new_pitcher"]
            if inning % 2 == 1:
                games.change_h_pitcher(id, new_pitcher)
                return redirect(url_for("game_page", id=id))
            else:
                games.change_a_pitcher(id, new_pitcher)
                return redirect(url_for("game_page", id=id))
                
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
            if at_bats.current_ab_id(id) is None:
                ab_id = at_bats.current_ab_id(id)
            else:
                ab_id = at_bats.last_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)

        elif "sl" in request.form:
            result = "Strike (looking)"
            if at_bats.current_ab_id(id) is None:
                ab_id = at_bats.current_ab_id(id)
            else:
                ab_id = at_bats.last_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)

        elif "ss" in request.form:
            result = "Strike (swinging)"
            if at_bats.current_ab_id(id) is None:
                ab_id = at_bats.current_ab_id(id)
            else:
                ab_id = at_bats.last_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)

        elif "Foul" in request.form:
            result = "Foul"
            if at_bats.current_ab_id(id) is None:
                ab_id = at_bats.current_ab_id(id)
            else:
                ab_id = at_bats.last_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)

        elif "Ball" in request.form:
            result = "Ball"
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
            if at_bats.current_ab_id(id) is None:
                ab_id = at_bats.current_ab_id(id)
            else:
                ab_id = at_bats.last_ab_id(id)
            at_bats.handle_pitch(result, ab_id, id, runners)

        elif "end_inning" in request.form:
            games.end_inning(id)

        elif "remove" in request.form:
            remove_id = request.form["remove"]
            games.remove_player(id, remove_id)
        
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

        # Make sure that both batting orders have at least 2 batters and only unique batters.
        error_message = games.validate_order(h_order, a_order)
        if error_message:
            return render_template("order.html", h_players=h_players, a_players=a_players, game_id=game_id,
                                   error_message=error_message, a_order=a_order, h_order=h_order,
                                   h_pitcher=h_pitcher, a_pitcher=a_pitcher)

        if games.set_order(game_id, h_order, a_order, h_pitcher, a_pitcher):
            return redirect(url_for("game_page", id=game_id))