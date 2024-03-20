from app import app
from flask import render_template, request, redirect
import users
import players
import teams
import leagues

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
    Process user input and add team to database
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