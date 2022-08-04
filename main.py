from flask import Flask, flash, redirect, render_template, request, session, make_response
from flask_session import Session
import os
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
import random
from helper import login_required
from datetime import datetime
# import matplotlib.pyplot as plt

# Configure application
app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = "Your_secret_string"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///users.db")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return redirect("/login")

            # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return redirect("/login")

            # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
                rows[0]["password"], request.form.get("password")):
            flash("invalid username and/or password")
            return redirect("/login")

            # Remember which user has logged in
        print(str(rows[0]["id"]))
        session['user_id'] = rows[0]["id"]
        print(session.get("user_id"))
        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        session.clear()
        # some variables
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")

        elif not request.form.get('password'):
            flash("must provide password")

        elif len(rows) != 0:
            flash("this username is already taken")
        else:
            db.execute("INSERT INTO users (username, password) VALUES(?, ?)",
                       username, password)
            # reset value of rows
            rows = db.execute("SELECT * FROM users WHERE username = ?",
                              request.form.get("username"))
            # Auto Login

            session['user_id'] = rows[0]["id"]
            return redirect("/")

        return redirect("/register")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


#the real stuff
@app.route('/')  # '/' for the default page (index)
def index():
    try:
        print(session.get("user_id"))
    except:
        pass
    return render_template("index.html")


@app.route('/about_us')
def about_us():
    return render_template("about_us.html")


@app.route('/my_info', methods=["GET", "POST"])
def my_info():
    time = datetime.date(datetime.now())
    if request.method == "POST":
        environment = request.form['environment']
        mood = request.form['feeling']
        rows = db.execute(
            "SELECT * FROM mood_tracker WHERE user_id = ? AND date = ?",
            session.get("user_id"), time)
        if len(rows) == 0:
            db.execute(
                "INSERT INTO mood_tracker (user_id, environment, mood, date) VALUES(?, ?, ?, ?)",
                session.get("user_id"), environment, mood, time)

    rows = db.execute(
        "SELECT * FROM mood_tracker WHERE user_id = ? AND date = ?",
        session.get("user_id"), time)
    submit = False
    if len(rows) != 0:
        submit = True
    else:
        submit = False

    mood_array = ["super_sad", "sad", "meh", "happy", "super_happy"]
    x = []
    y = []
    rows = db.execute("SELECT * FROM mood_tracker WHERE user_id = ?",
                      session.get("user_id"))
    for row in rows:
        x.append(row["date"])
        y.append(mood_array.index(row["mood"]) + 1)
    # print(x)
    # print(y)
    # plt.plot(x, y, "bo")
    # plt.xlabel('Date')
    # plt.ylabel('Mood')
    # plt.title(rows["environment"])
    # plt.savefig("graphs/"+session["user_id"]+".jpg")

    username = db.execute("SELECT * FROM USERS WHERE id = ?",
                          session.get("user_id"))[0]["username"]
    return render_template("my_info.html", username=username, submit=submit)


@app.route('/global_stats')
def global_stats():
    return render_template("global_stats.html")


#idk what this is but it works
if __name__ == "__main__":
    # Makes sure this is the main process
    app.run(  # Starts the site
        host=
        '0.0.0.0',  # EStablishes the host, required for repl to detect the site
        port=2000  # Randomly select the port the machine hosts on.
    )

#THANK YOU STACKOVERFLOW!!!!!!!!!!
# * Running on http://127.0.0.1:2000
# * Running on http://172.18.0.10:2000
