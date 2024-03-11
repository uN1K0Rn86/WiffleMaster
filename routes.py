from app import app
from flask import render_template, request, redirect
import users
import players

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
            player_list = players.display_players()
            return render_template("players.html", player_list=player_list, message="Player added")
        else:
            return render_template("error.html", message="Could not add player. Did you provide all the information?")
        