import os
import cs50
import string

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_stocks = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM history WHERE user_id = ? GROUP BY symbol", session["user_id"])
    user_cash = db.execute("SELECT users.cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Update to current value each share unit of each symbol
    updated_portfolio = []
    for stock in user_stocks:
        updated_stock = lookup(stock["symbol"])
        total = stock["total_shares"] * updated_stock["price"]
        data = {}
        data["symbol"] = updated_stock["symbol"]
        data["name"] = updated_stock["name"]
        data["shares"] = stock["total_shares"]
        data["price"] = updated_stock["price"]
        data["total"] = total
        updated_portfolio.append(data)

    # Sum all earnings
    quote_accumulated = 0
    for quote in updated_portfolio:
        quote_accumulated += quote["total"]

    portfolio_total = quote_accumulated + user_cash

    return render_template("index.html", updated_portfolio=updated_portfolio, user_cash=user_cash, portfolio_total=portfolio_total)


@app.route("/cash", methods=["POST"])
@login_required
def cash():
    """Add more cash"""
    cash_required = request.form.get("cash")
    user_cash = db.execute("SELECT users.cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    if int(cash_required) <= 0:
        return apology("cash must be positive", 400)
    else:
        total_cash = int(cash_required) + user_cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", total_cash, session["user_id"])
        return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("missing symbol", 400)
        if not shares:
            return apology("missing shares", 400)

        for char in shares:
            # checking whether the char is punctuation.
            if char in string.punctuation:
                return apology("invalid shares with punctuation", 400)

        if any(c.isalpha() for c in shares):
            return apology("invalid shares with text", 400)

        if int(shares) <= 0:
            return apology("invalid shares", 400)

        quote = lookup(symbol)
        if quote == None:
            return apology("invalid symbol", 400)
        else:
            current_price = quote["price"]
            user_cash = db.execute("SELECT users.cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            remainder_cash = user_cash - (int(shares) * current_price)
            if remainder_cash < 0:
                return apology("can't afford", 400)
            else:
                db.execute("UPDATE users SET cash = ? WHERE id = ?", remainder_cash, session["user_id"])
                db.execute("INSERT INTO history (symbol, shares, price, user_id) VALUES(?, ?, ?, ?)",
                           quote["symbol"], shares, current_price, session["user_id"])
                return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_history = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
    return render_template("history.html", user_history=user_history)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)
        quote = lookup(symbol)
        if quote == None:
            return apology("invalid symbol", 400)
        else:
            return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password and confirmation were submitted
        elif not password or not confirmation:
            return apology("must provide both password and confirmation", 400)

        # Ensure passwords match
        elif not password == confirmation:
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username not exists
        if len(rows) >= 1:
            return apology("invalid username, it already exists", 400)

        # Generate password hash and save new user to database
        else:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Redirect user to login page
            return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_stocks = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM history WHERE user_id = ? GROUP BY symbol", session["user_id"])

    if request.method == "POST":
        # Validate if user not selected stock, share or no-owned stock
        stock_selected = request.form.get("symbol")
        shares_selected = request.form.get("shares")
        if not stock_selected:
            return apology("missing symbol", 400)
        if not shares_selected:
            return apology("missing shares", 400)
        # Check if stock selected exists in user's portfolio
        if not any(stock["symbol"] == stock_selected for stock in user_stocks):
            return apology("symbol not owned", 400)

        for char in shares_selected:
            # checking whether the char is punctuation.
            if char in string.punctuation:
                return apology("invalid shares with punctuation", 400)

        if any(c.isalpha() for c in shares_selected):
            return apology("invalid shares with text", 400)

        # Validate if share number not positive or no-owned share number
        if int(shares_selected) <= 0:
            return apology("shares must be positive", 400)
        owned_shares = 0
        for stock in user_stocks:
            if stock["symbol"] == stock_selected:
                owned_shares = stock["total_shares"]
        if int(shares_selected) > owned_shares:
            return apology("too many shares", 400)

        else:
            # Add stock current price to user's cash
            current_price = lookup(stock_selected)["price"]
            user_cash = db.execute("SELECT users.cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

            new_cash = user_cash + (int(shares_selected) * current_price)

            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])
            db.execute("INSERT INTO history (symbol, shares, price, user_id) VALUES(?, ?, ?, ?)",
                       stock_selected, -int(shares_selected), current_price, session["user_id"])

            return redirect("/")
    else:
        return render_template("sell.html", user_stocks=user_stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
