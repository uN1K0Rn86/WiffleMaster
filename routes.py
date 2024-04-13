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
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong username or password")
        
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
        if password1 != password2:
            return render_template("error.html", message="Passwords do not match")
        if users.register(username, password1):
            return redirect("/")
        else:
            return render_template("error.html", message="Registration was not successful")
        
@app.route("/logout")
def logout():
    """Call the logout function.
    Redirect to the home page.
    """
    users.logout()
    return redirect("/")

@app.route("/players", methods=["GET", "POST"])
def go_players():
    """Return the template for players.html.
    Process user input and add player to database.
    """
    if request.method == "GET":
        player_list = players.display_players()
        return render_template("players.html", player_list=player_list)
    if request.method == "POST":
        name = request.form["name"]
        try:
            bats = request.form["bats"]
        except:
            return render_template("error.html", message="Please select a value for batting handedness.")
        try:
            throws = request.form["throws"]
        except:
            return render_template("error.html", message="Please select a value for throwing handedness.")
        if players.add_player(name, bats, throws):
            return redirect("/players")
        else:
            return render_template("error.html", message="Could not add player. Did you provide all the information?")
        
@app.route("/players/<int:id>")
def player_page(id):
    player = players.display_player(id)
    return render_template("player.html", player=player)

@app.route("/teams", methods=["GET", "POST"])
def go_teams():
    """Return the template for teams.html.
    Process user input and add team to database.
    """
    if request.method == "GET":
        team_list = teams.show_teams()
        return render_template("teams.html", team_list=team_list)
    if request.method == "POST":
        name = request.form["name"]
        if teams.add_team(name):
            return redirect("/teams")
        else:
            return render_template("error.html", message="Could not create team")
        
@app.route("/teams/<int:id>", methods=["GET", "POST"])
def team_page(id):
    if request.method == "GET":
        team = teams.show_team(id)
        team_players = teams.list_players(id)
        teamless = players.list_teamless()
        others = teams.list_players_other(id)
        return render_template("team.html", team=team, team_players=team_players, teamless=teamless, others=others)
    if request.method == "POST":
        team_id = id
        direct = f"/teams/{id}"
        if "players" in request.form:
            player_id = request.form["players"]
            if teams.add_player(player_id, team_id):
                return redirect(direct)
            else:
                return render_template("error.html", message="Could not add player")
        elif "move" in request.form:
            move_p_id = request.form["move"]
            if teams.move_player(move_p_id, team_id):
                return redirect(direct)
            else:
                return render_template("error.html", message="Could not move player")
        else:
                return render_template("error.html", message="Could not add player")
        
@app.route("/leagues", methods=["GET", "POST"])
def go_leagues():
    """Return the template for leagues.html.
    Process user input and add a league to database
    """
    if request.method == "GET":
        league_list = leagues.show_leagues()
        return render_template("leagues.html", league_list=league_list)
    if request.method == "POST":
        name = request.form["name"]
        if leagues.add_league(name):
            return redirect("/leagues")
        else:
            return render_template("error.html", message="Could not create league")
        
@app.route("/leagues/<int:id>", methods=["GET", "POST"])
def league_page(id):
    """Return the template for the league in question."""
    if request.method == "GET":
        league = leagues.show_league(id)
        league_teams = leagues.show_teams(id)
        others = leagues.show_other_teams(id)
        return render_template("league.html", league=league, league_teams=league_teams, others=others)
    if request.method == "POST":
        team = request.form["team"]
        direct = f"/leagues/{id}"
        if leagues.add_team(team, id):
            return redirect(direct)
        else:
            return render_template("error.html", message="Could not add team to league")
        
@app.route("/games", methods=["GET", "POST"])
def go_games():
    """Return the template for creating games."""
    if request.method == "GET":
        all_teams = teams.show_teams()
        all_leagues = leagues.show_leagues()
        in_progress = games.games_in_progress()
        return render_template("games.html", all_teams=all_teams, all_leagues=all_leagues, in_progress=in_progress)
    if request.method == "POST":
        a_team_id = request.form["a_team"]
        h_team_id = request.form["h_team"]
        league_id = request.form["league"]
        innings = request.form["innings"]
        if a_team_id == h_team_id:
            return render_template("error.html", message="Please choose two different teams")
        game_id = games.new_game(innings, a_team_id, h_team_id, league_id)
        if not game_id:
            return render_template("error.html", message="Game creation failed.")
        else:
            return redirect(url_for("go_order", game_id=game_id))

@app.route("/games/<int:id>", methods=["GET", "POST"])
def game_page(id):
    """Return the page for the game in question."""
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
    print(inning)
    
    if request.method == "GET":
        if inning % 2 == 1:
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    last = games.get_a_previous(id)
                    if last >= len(a_order) - 2:
                        games.set_a_previous(id, -1)
                    else:
                        games.set_a_previous(id, last+1)
            previous = games.get_a_previous(id)
            batter = games.batter_up(a_order, previous)
            batter_stats = games.batting_stats(id, batter[0])
            on_deck = games.batter_up(a_order, previous+1)
            on_deck_stats = games.batting_stats(id, on_deck[0])
            pitcher = h_pitcher
            p_players = teams.list_players(h_team[0])
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    at_bats.create_at_bat(id, batter[0], pitcher[0], h_team[0], a_team[0])
            ab_id = at_bats.current_ab_id(id)
            if in_progress:
                count = (at_bats.balls(ab_id), at_bats.strikes(ab_id))
            else:
                count = (0, 0)
            pitch_count = games.pitch_count(id, h_pitcher[0])
            
        else:
            if in_progress:
                if at_bats.current_ab_id(id) is None:
                    last = games.get_h_previous(id)
                    if last >= len(h_order) - 2:
                        games.set_h_previous(id, -1)
                    else:
                        games.set_h_previous(id, last+1)
            previous = games.get_h_previous(id)
            batter = games.batter_up(h_order, previous)
            batter_stats = games.batting_stats(id, batter[0])
            on_deck = games.batter_up(h_order, previous+1)
            on_deck_stats = games.batting_stats(id, on_deck[0])
            pitcher = a_pitcher
            p_players = teams.list_players(a_team[0])
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
        elif "pitch" in request.form:
            result = request.form["pitch"]
            runners = []
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
    h_team = games.home_team(game_id)
    a_team = games.away_team(game_id)
    if request.method == "GET":
        h_players = teams.list_players(h_team[0])
        a_players = teams.list_players(a_team[0])
        return render_template("order.html", h_players=h_players, a_players=a_players, game_id=game_id)
    if request.method == "POST":
        h_order = request.form.getlist("h_order")
        h_order = [player for player in h_order if player != "None"]
        h_order = [int(player_id) for player_id in h_order]
        if len(h_order) != len(set(h_order)):
            return render_template("error.html", message="Please select only unique batters")
        h_pitcher = request.form["h_pitcher"]
        a_order = request.form.getlist("a_order")
        a_order = [player for player in a_order if player != "None"]
        a_order = [int(player_id) for player_id in a_order]
        if len(a_order) < 2 or len(h_order) < 2:
            return render_template("error.html", message="Please select at least 2 batters")
        if len(a_order) != len(set(a_order)):
            return render_template("error.html", message="Please select only unique batters")
        a_pitcher = request.form["a_pitcher"]
        if games.set_order(game_id, h_order, a_order, h_pitcher, a_pitcher):
            return redirect(url_for("game_page", id=game_id))
        else:
            return render_template("error.html", message="Could not set batting order")