import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd
import numpy as np

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


STOCKS = {}



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    # get portfolio of stocks
    wallet = db.execute("SELECT SUM (stocks_quantity), symbol from stocks where logIn_id = ? group by symbol", session["user_id"])
    quantity = db.execute("SELECT (stocks_quantity), symbol  from stocks where logIn_id = ? ", session["user_id"])

    i = 0
    Azioni = []
    for x in wallet:
        Azioni.append(lookup(wallet[i].get('symbol')))
        i = i + 1

    # calculating the * of current price with stock owned
    total = []

    i = 0
    for stock in wallet:

        tot_val = lookup(stock["symbol"])["price"] * stock["SUM (stocks_quantity)"]

        total.append(tot_val)

    # total of stock with current price
    totale = {}
    totale = np.array([{'name': round(float(i),2)} for i in total])

    totaleOfStock = sum(d['name'] for d in totale)

    # total of cash into bank account
    balance = (db.execute ("SELECT cash FROM users WHERE id = ?", session["user_id"]))
    tot = balance[0].get('cash')


    #total of cash and stock
    cashStock = float(tot) + float(totaleOfStock)
    cash = cashStock
    cash = usd(cash)
    tot = usd(tot)

    return render_template("index.html", wallet=wallet, tot=tot,  Azioni=Azioni, totale=totale, cashStock=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # POST method will buy stock if enough money
    if request.method == "POST":

        # validating  the form
        if not request.form.get("symbol") or not request.form.get("quantity"):
            return apology("must provide symbol and quantity", 400)

        # find the symbol to search
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        stocks = {}
        stocks = lookup(sigla)
        if stocks == None:
            return apology("Stocks symbol not found", 403)

        # getting the total amount of stock ans check with banck account
        price = float(stocks.get("price"))
        q = float(request.form.get("quantity"))
        total = (price * q)

        bankAmount = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"] )
        deposit = float(bankAmount[0]["cash"])

        # new amount in bank
        newAmount = deposit - total

        now = datetime.today().isoformat()

        # insert every single buy as a line not as a total
        n = int(q)

        if total > deposit:
            return apology("Not enough money", 403)
        else:
            for i in range(n):
                 insert = db.execute("INSERT INTO stocks (symbol, stocks_quantity, price_stock, logIn_id) VALUES (?,?,?,?)", sigla, 1, price, session["user_id"])
            update = db.execute("UPDATE users SET cash = ?  WHERE id = ?", newAmount , session["user_id"] )
            history = db.execute("INSERT INTO history (user_id, symbol, price, shares, transacted) VALUES (?,?,?,?,?)", session["user_id"], sigla, price, q, now)
            return redirect("/")

    # Get method will display form to buy stock
    else:
        return render_template("buy.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    """Show history of transactions"""
    if request.method == "POST" or request.method == "GET":
        history = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])


    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

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

    # request by POST subimit the search
    if request.method == "POST":
        # find the symbol to search
         sigla = request.form.get("symbol")
         #stocks = {}
         STOCKS = lookup(sigla)

         if STOCKS == None:
            return apology("Stocks symbol not found", 400)
         else:
            return render_template("quoted.html", stocks = STOCKS)


    # submit via GET render display form to request a stock quote
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # if post check for possible errors
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # check the confirmation password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("confirmation password must be the same", 400)

        # hash the password
        hash = generate_password_hash(request.form.get("password"),method='pbkdf2:sha256', salt_length=8)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is free
        if len(rows) != 0:
            return apology("Username is already taken", 400)

        # Insert user into DB
        insert = db.execute("INSERT INTO users (username,hash) VALUES (?,?)", request.form.get("username") , hash)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    # when requested via get display registration form
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    """Sell shares of stock"""

      # post request must update and check db
    if request.method == "POST":


        # validating  the form
        if not request.form.get("symbol") or not request.form.get("quantity"):
            return apology("must provide symbol and quantity", 400)

        # find the symbol to search
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        stocks = {}
        stocks = lookup(sigla)
        if stocks == None:
            return apology("Stocks symbol not found", 403)


        # getting the total amount of stock ans check with banck account
        price = float(stocks.get("price"))
        q = float(request.form.get("quantity"))
        total = (price * q)

        bankAmount= db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        deposit = float(bankAmount[0]["cash"])

        # new amount in bank
        newAmount = deposit + total

        # number of share owned
        countShare = db.execute("select symbol,SUM(stocks_quantity) from stocks where logIn_id = ? AND symbol = ? group by symbol;", session["user_id"], sigla )

        shareNumber = float(countShare[0]['SUM(stocks_quantity)'])

        now = datetime.today().isoformat()
        a = -(q)

        # if you want to sell more then what you have NO!
        if q > shareNumber :
            return apology("Not enough share", 403)


        shareOwned = db.execute("select id, stocks_quantity from stocks where logIn_id = ? AND symbol = ? ", session["user_id"], sigla)


        # quantity of stocks to sell
        n = int(q)

        for i in range(n):
            updateStock = db.execute("UPDATE stocks SET stocks_quantity= ? WHERE logIn_id = ? AND symbol = ? AND id = ?", 0, session["user_id"], sigla, shareOwned[i]["id"])

        updateBalance = db.execute("UPDATE users SET cash = ? where id = ?", newAmount, session["user_id"])
        history = db.execute("INSERT INTO history (user_id, symbol, price, shares, transacted) VALUES (?,?,?,?,?)", session["user_id"], sigla, price, a, now)

        n_shares = db.execute ("SELECT stocks_quantity FROM stocks WHERE logIn_id = ?", session["user_id"])
        deleting = db.execute ("DELETE FROM stocks WHERE stocks_quantity = 0")


        return redirect("/")

    # when requested via get display sell form
    else:
        return render_template("sell.html")
