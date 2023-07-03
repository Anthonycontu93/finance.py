import os
import requests
from cs50                       import SQL
from flask                      import Flask, flash, redirect, render_template, request, session
from flask_session              import Session
from tempfile                   import mkdtemp
from werkzeug.security          import check_password_hash, generate_password_hash
from config                     import *
from alpaca.trading.client      import TradingClient
from alpaca.trading.requests    import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums       import OrderSide, TimeInForce
from alpaca.trading.enums       import AssetClass
from alpaca.data.historical     import CryptoHistoricalDataClient
from alpaca.data.requests       import *
from alpaca.data.timeframe      import TimeFrame
from alpaca.data.live           import CryptoDataStream
import datetime
from datetime                   import date, timedelta
import pandas                   as pd
import json


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///clienti.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# new class client
#trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


# Getting account information always available
#account = trading_client.get_account()

# client history class always available
#client = CryptoHistoricalDataClient()


# Get all the stocks
#positions = trading_client.get_all_positions()



@app.route("/")
@login_required
def index():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()

    #Check if our account is restricted from trading.
    if account.trading_blocked:
        return apology("Account blocked, try to regenerate API KEY", 400)

    # Get all the stocks
    positions = trading_client.get_all_positions()


    sigla = []
    chart_pie = []
    chart_pieN = []
    for stocks in positions:
        sigla.append(stocks.symbol)
        sigla.append(stocks.current_price)
        chart_pie.append(stocks.symbol)
        chart_pieN.append(stocks.qty)

    data = json.dumps(chart_pie)
    number_of_share = json.dumps(chart_pieN)

    for property_name, value in account:
        if property_name == "cash":
            cash = round(float(value), 2)
    for property_name, value in account:
        if property_name == "equity":
            equity = round(float(value), 2)
    for property_name, value in account:
        if property_name == "last_equity":
            last_equity = round(float(value), 2)


    return render_template("index.html", wallet = positions, cash = cash, equity = equity, sigla = sigla, last_equity = last_equity , data = data , number_of_share = number_of_share)

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()

    # get method will show the html quote page
    if request.method == "GET":
        return render_template("quote.html")

    else:


        # search for US equities and cryptocurrency with post method
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        symbol = str(sigla)


    try:
        search_params = trading_client.get_asset(symbol)
        # response = requests.get(search_params)
        # response.raise_for_status()

        for parameter, value in search_params:
            if parameter == "name":
                name = str(value)
        for parameter, value in search_params:
            if parameter == "symbol":
                symbol = str(value)


        if search_params.tradable:
            return render_template("tradable.html", symbol = symbol, name = name)


    except:
        return render_template("noTrade.html")



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()




    # POST method will buy stock if enough money
    if request.method == "POST":

        # validating  the form
        if not request.form.get("symbol") or not request.form.get("qty"):
            return apology("must provide symbol and quantity", 400)


        # search for US equities and cryptocurrency symbol
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        symbol = str(sigla)

        # get the qty of stocks/crypto
        quantity = request.form.get("qty")
        qty = int(quantity)


        try:

            search_params = trading_client.get_asset(symbol)
            if search_params.tradable:
                # preparing the market order
                market_order_data = MarketOrderRequest(symbol= symbol,
                qty = qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY)

                # Market order
                market_order = trading_client.submit_order(order_data = market_order_data)
                return redirect("/")

        except:
            return render_template("noTrade.html")



    # Get method will display form to buy stock
    else:
        return render_template("buy.html")



@app.route("/crypto", methods=["GET", "POST"])
@login_required
def buycrypto():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()



    # POST method will buy stock if enough money
    if request.method == "POST":

        # validating  the form
        if not request.form.get("symbol") or not request.form.get("qty"):
            return apology("must provide symbol and quantity", 400)


        # search for US equities and cryptocurrency symbol
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        symbol = str(sigla)

        # get the qty of stocks/crypto
        quantity = request.form.get("qty")
        qty = int(quantity)


        search_params = trading_client.get_asset(symbol)

        if search_params.tradable:


            # preparing the market order
            market_order_data = MarketOrderRequest(symbol= symbol,
            qty = qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC)

            # Market order
            market_order = trading_client.submit_order(order_data = market_order_data)

            return redirect("/")



    # Get method will display form to buy stock
    else:
        return render_template("crypto.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()



    """Sell shares of stock"""

      # post request must update and check db
    if request.method == "POST":


        # validating  the form
        if not request.form.get("symbol") or not request.form.get("quantity"):
            return apology("must provide symbol and quantity", 400)

        # find the symbol to search
        sigla = request.form.get("symbol")
        sigla = sigla.upper()
        qty_i_want_to_sell = request.form.get("quantity")
        qty_to_sell = int(qty_i_want_to_sell)



        # Check on our asset
        positions = trading_client.get_all_positions()
        qty = 0

        # check quantity of stocks
        for stock in positions:
            if stock.symbol == sigla:
                qty = stock.qty

        # round the decimals
        qty = float(qty)
        qty = round((qty), 3)

        if qty < qty_to_sell:
            return apology("Not enough stocks",400)


        # preparing orders
        market_order_data = MarketOrderRequest(
                 symbol=sigla,
                 qty=qty_to_sell,
                 side=OrderSide.SELL,
                 time_in_force=TimeInForce.GTC
              )

        # Market order
        market_order = trading_client.submit_order(
             order_data=market_order_data
             )



        return redirect("/")

    # when requested via get display sell form
    else:
        return render_template("sell.html")



@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    # get API and SECRET KEY
    #@login_required
    APIKEY = db.execute("SELECT apikey FROM client WHERE id = ?", session["user_id"])
    SECRETKEY = db.execute("SELECT secretkey FROM client WHERE id = ?", session["user_id"])

    API_KEY = str(APIKEY[0]["apikey"])
    SECRET_KEY = str(SECRETKEY[0]["secretkey"])


    # new class client
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

    account = trading_client.get_account()

    client = CryptoHistoricalDataClient()

    positions = trading_client.get_all_positions()


    if request.method == "GET":
        return render_template("history.html")

    # request by POST subimit the search
    if request.method == "POST":


        # find the symbol to search
        sigla = request.form.get("symbol/pair")
        sigla = sigla.upper()

        if sigla == None:
            return apology("Stocks symbol not found", 400)

        # get the date from and to
        x = request.form.get("time-from")
        y = request.form.get("time-to")


        datafrom = x.split("-")
        datato = y.split("-")


        if datetime.date(int(datafrom[0]),int(datafrom[1]),int(datafrom[2])) > datetime.date(int(datato[0]), int(datato[1]), int(datato[2])):
            return render_template("wrongdata.html")

        # Creating request object for understanding the asset
        request_params = CryptoBarsRequest (
                    symbol_or_symbols= sigla,
                    timeframe= TimeFrame.Day,
                    start= datetime.datetime(int(datafrom[0]), int(datafrom[1]), int(datafrom[2])),
                    end= datetime.datetime(int(datato[0]), int(datato[1]), int(datato[2])))

        # Retrieve daily bars for cryptoAsset in a DataFrame and printing it
        btc_bars = client.get_crypto_bars(request_params)
        data = pd.DataFrame(btc_bars.df)
        open = data["open"]
        high = data["high"]
        low = data["low"]
        close = data["close"]
        trade_count = data["trade_count"]
        vwap = data["vwap"]


        x = len(vwap)
        numb = []
        for i in range(x):
            numb.append(i)


        return render_template("trend.html", open=open, high=high, low=low, close=close, sigla=sigla, trade_count=trade_count, vwap = vwap, numb = numb)



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
        rows = db.execute("SELECT * FROM client WHERE username = ?", request.form.get("username"))

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

        #Ensure api key and secret key are submitted
        elif not request.form.get("APIKEY"):
            return apology("must insert API KEY", 400)

        #Ensure api key and secret key are submitted
        elif not request.form.get("SECRETKEY"):
            return apology("must insert SECRET KEY", 400)


        # check the confirmation password
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("confirmation password must be the same", 400)

        # hash the password
        hash = generate_password_hash(request.form.get("password"),method='pbkdf2:sha256', salt_length=8)

        #get value of API KEY and SECRET KEY
        apikey = request.form.get("APIKEY")
        secretkey = request.form.get("SECRETKEY")

        # Query database for username
        rows = db.execute("SELECT * FROM client WHERE username = ?", request.form.get("username"))

        # Ensure username is free
        if len(rows) != 0:
            return apology("Username is already taken", 400)

        # Insert user into DB
        insert = db.execute("INSERT INTO client (username, hash, apikey, secretkey) VALUES (?,?,?,?)", request.form.get("username"), hash, apikey, secretkey)

        # Query database for username
        rows = db.execute("SELECT * FROM client WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    # when requested via get display registration form
    else:
        return render_template("register.html")


