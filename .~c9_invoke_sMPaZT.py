import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
# export API_KEY=pk_5dd3c497a8f349afb35628edd13adfc1
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    stocks = db.execute("SELECT * FROM purchase WHERE users_id =:id GROUP BY symbol", id=session["user_id"])
    if len(stocks) != 1:
        return apology("An error occured please try again", 400)
    # # return jsonify(stocks)
    
    purchase ={}
    for stock in stocks:
        purchase["symbol"] = stock["symbol"]
        purchase["symbol"] share = stock["share"]
        purchase[] = usd(lookup(stock["symbol"])["price"])
        time = stock["transaction_time"]
    # , symbol=symbol, share=share, price=price,time=time
    return render_template("portfolio.html", stocks=stocks)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # return apology("TODO")

    user_id = session["user_id"]

    if request.method ==  "POST":
        shares = request.form.get("shares")
        stock = lookup(request.form.get("symbol"))

        if not stock or stock == False:
            return apology("Please input a valid stock", 400)

        if not shares.isdigit() or int(request.form.get("shares")) <= 0:
            return apology("Share was not specified.", 400)

        prices = stock["price"]
        price = prices.isdigit()

        balance_cash = float(db.execute("SELECT cash FROM users WHERE id =?", user_id)[0]["cash"])

        total = price * shares
        cash = balance_cash - total

        if cash < balance_cash:
            return apology("Sorry!! Low balance", 400)

        # update user's cash
        db.execute(f"UPDATE users SET cash = {cash} WHERE id = {user_id}")

        # Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price.
        # Store enough information so that you know who bought what at what price and when.
        db.execute("INSERT INTO  purchase (users_id, symbol, price, share, transaction_time) VALUES(?, ?, ?, ?, datetime('now'))", user_id, stock["symbol"], price, shares)

        # When a purchase is complete, redirect the user back to the index page.
        return redirect("/")

    else:
        return render_template("buy.html")
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # return apology("TODO")
    return render_template("history.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# TODO for QUOTE
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    stock = request.form.get("symbol")
    symbol = lookup(str(stock))
    if request.method ==  "POST":

        if not symbol or symbol == False:
            return apology("Symbol not specified", 400)
        else:
            return render_template("quoted.html", symbol=symbol)
    else:
        # return jsonify()
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Get user info
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation_pwd = request.form.get("confirmation")
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    user = validateUser(rows)
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # confirm password was submitted
        elif confirmation_pwd != password:
            return apology("Password not match", 400)

         # Remove duplicate users.
        elif user == username:
            return apology("Username already exist", 400)
        else:
            # submit registration
            db.execute("INSERT INTO  users (username, hash ) VALUES(?, ?)", username,  generate_password_hash(password, method='pbkdf2:sha256', salt_length=8))
            # Redirect user to login page
            return redirect("/login")

    else:
        # Send registration page
        return render_template("register.html")
def validateUser(rows):
    for index in range(len(rows)):
        return rows[index]["username"]

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # return apology("TODO")

    if request.method ==  "POST":
        shares = request.form.get("shares")
        symbols = lookup(request.form.get("symbol"))
        if not lookup(request.form.get("symbol")) or lookup(request.form.get("symbol")) == False:
            return apology("No stock was specified.", 400)

        if not shares.isdigit() or shares.isdigit() <= 0:
            return apology("Share was not specified.", 400)

        return render_template("sold.html", symbol=symbol, shares=shares)
    else:
        return render_template("sell.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
