from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
import datetime

from helpers import plot_data, get_ohlcv, login_required, inr
from news import get_news

# Configure application
app = Flask(__name__)
app.secret_key = 'super secret key'

# Configure SQL
mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="jjfinance")
crsr=mydb.cursor()

@app.route("/")
def home():
    """ Home page """
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ Sign user up """
    
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash(u"Must provide username","error")
            return render_template("signup.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash(u"Must provide password","error")
            return render_template("signup.html")

        # ensure passconfirm was submitted
        elif not request.form.get("confirmation"):
            flash(u"Must confirm password","error")
            return render_template("signup.html")

        # ensure password and passconfirm are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            flash(u"passwords do not match","error")
            return render_template("signup.html")

        # check if username already exists
        crsr.execute("SELECT username FROM users WHERE username = '{}'".format(request.form.get("username")))
        rows = crsr.fetchall()

        l1 = []
        for i in rows:
            for j in i:
                l1.append(j)

        if request.form.get("username") in l1:
            flash(u"Username already exists","error")
            return render_template("signup.html")

            
        # hash password
        hashpass = generate_password_hash(request.form.get("password"))

        # enter username in database
        crsr.execute("INSERT INTO users (username, password) VALUES ('{}', '{}')".format(request.form.get("username"), hashpass))
        mydb.commit()

        # query database for username
        crsr.execute("SELECT id FROM users WHERE username = '{}'".format(request.form.get("username")))
        rows = crsr.fetchall()

        # remember which user has logged in
        session["user_id"] = rows[0][0]

        # redirect user to home page
        return redirect("/")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Logs user in """

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash(u"Must provide username","error")
            return render_template("signup.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash(u"must provide password","error")
            return render_template("signup.html")

        # check if username exists in database
        crsr.execute("SELECT username FROM users WHERE username = '{}'".format(request.form.get("username")))
        rows = crsr.fetchall()

        l1 = []
        for i in rows:
            for j in i:
                l1.append(j)

        if request.form.get("username") not in l1:
            flash(u"Username does not exist","error")
            return render_template("login.html")
        
        # ensure username and password match
        crsr.execute("SELECT password FROM users WHERE username = '{}'".format(request.form.get("username")))
        rows = crsr.fetchall()

        if not check_password_hash(rows[0][0], request.form.get("password")):
            flash(u"Username and password do not match","error")
            return render_template("login.html")

        # FOR REMEMBERING USER
        # query database for username
        crsr.execute("SELECT id FROM users WHERE username = '{}'".format(request.form.get("username")))
        rows = crsr.fetchall()

        # remember which user has logged in
        session["user_id"] = rows[0][0]

        # redirect user to home page
        return redirect("/")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/portal", methods=['GET', 'POST'])
def portal():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if Quote was not submitted
        if not request.form.get("Quote"):
            flash(u"Must provide symbol","error")
            return render_template("portal.html")

        symbol = request.form.get("Quote")

        # getting latest data in case market is closed (for whatever reason)
        today = datetime.date.today()
        date = today
        strdate = datetime.date.today().strftime("%d-%m-%Y")

        while True:
            try:
                df = get_ohlcv(symbol, strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            # if incorrect symbol given
            except:
                flash(u"Please enter valid symbol","error")
                return render_template("portal.html")
            break
            
        symbolDict = df.to_dict('records')[0]

        # creating a html page with a graph
        startdate = '01-01-2002'
        plot_data(symbol, startdate)
        
        return render_template("portal.html", symbolDict = symbolDict, symbol = symbol)      

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("portal.html")
    

@app.route("/watchlist", methods=['GET','POST'])
@login_required
def watchlist():
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if Quote was not submitted
        if not request.form.get("Quote"):
            flash(u"Must provide symbol","error")
            return render_template("watchlist.html")

        symbol = request.form.get("Quote")

        # getting latest data in case market is closed (for whatever reason)
        today = datetime.date.today()
        date = today
        strdate = datetime.date.today().strftime("%d-%m-%Y")

        while True:
            try:
                df = get_ohlcv(symbol, strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            # if incorrect symbol given
            except:
                flash(u"Please enter valid symbol","error")
                return redirect("/watchlist")
            break
        
        # inserting new symbol into the watchlist
        crsr.execute("INSERT INTO watchlist (symbol, userid) VALUES ('{}', {})".format(symbol, session["user_id"]))
        mydb.commit()

        # getting all symbols from the watchlist table
        crsr.execute("SELECT symbol FROM watchlist where userid = {}".format(session["user_id"]))
        rows = crsr.fetchall()
        
        symbolDictList = []
        symbolList = []
        for row in rows:
            df = get_ohlcv(row[0], strdate)
            symbolDict = df.to_dict('records')[0]
            
            symbolDictList.append(symbolDict)
            symbolList.append(row[0])

        return render_template("watchlist.html", symbolDictList = symbolDictList, symbolList = symbolList)
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        
        # getting all symbols from the watchlist table
        crsr.execute("SELECT symbol FROM watchlist where userid = {}".format(session["user_id"]))
        rows = crsr.fetchall()
         
        # getting the latest date when we have data
        today = datetime.date.today()
        date = today
        strdate = datetime.date.today().strftime("%d-%m-%Y")

        while True:
            try:
                df = get_ohlcv('SBIN', strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            break

        symbolDictList = []
        symbolList = []
        for row in rows:
            df = get_ohlcv(row[0], strdate)
            symbolDict = df.to_dict('records')[0]
            
            symbolDictList.append(symbolDict)
            symbolList.append(row[0])

        return render_template("watchlist.html", symbolDictList = symbolDictList, symbolList = symbolList)


@app.route("/news")
def news():
    dict_news = get_news()

    return render_template('news.html', dict_news = dict_news)

    
@app.route("/currency")
def currency():
    return render_template('currency.html')
    

@app.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if Quote was not submitted
        if not request.form.get("Quote"):
            flash(u"Must provide symbol","error")
            return render_template("buy.html")

        #if shares not submitted
        if not request.form.get("Number"):
            flash(u"Must provide number of shares","error")
            return render_template("buy.html")

        
        symbol = request.form.get("Quote")
        shares = eval(request.form.get("Number"))

        #if not an integer in shares
        if type(eval(request.form.get("Number"))) != int:
            flash(u"Must provide a number","error")
            return render_template("buy.html")



        # getting latest data in case market is closed (for whatever reason)
        today = datetime.date.today()
        date = today
        strdate = datetime.date.today().strftime("%d-%m-%Y")

        while True:
            try:
                df = get_ohlcv(symbol, strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            # if incorrect symbol given
            except:
                flash(u"Please enter valid symbol","error")
                return render_template("buy.html")
            break
            
        symbolDict = df.to_dict('records')[0]


        #Inserting data in history table
        crsr.execute("INSERT INTO history (Symbol, Shares, Price, Date_Time, UserId) VALUES ('{}',{}, {}, '{}', {})".format(symbol, shares, symbolDict["Close"], datetime.datetime.now(), session["user_id"] ))
        mydb.commit()

        #Inserting data in portfolio
        crsr.execute("Select symbol from portfolio where userID = {}".format(session['user_id']))
        symbols_present = crsr.fetchall()

        existing_symbols = []
        for i in symbols_present:
            for j in i:
                existing_symbols.append(j)

        print(existing_symbols)

        if symbol in existing_symbols:
            crsr.execute("Update Portfolio set shares = shares + {} where userId = {} and symbol = '{}'".format(shares, session['user_id'], symbol))
            mydb.commit()

            
        else:
            crsr.execute("INSERT INTO portfolio(Symbol, Shares,  UserId) VALUES ('{}',{}, {})".format(symbol, shares, session["user_id"] ))
            mydb.commit()

        #Decrease Cash
        totalprice = shares*int(symbolDict["Close"])
        print(totalprice)

        crsr.execute("Update Users Set Cash = Cash - {} where Id = {}".format(totalprice, session['user_id']))
        mydb.commit()
        

        return render_template("buy.html", symbolDict = symbolDict, symbol = symbol, shares = shares)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")

@app.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if Quote was not submitted
        if not request.form.get("Quote"):
            flash(u"Must provide symbol","error")
            return render_template("sell.html")

        #if shares not submitted
        if not request.form.get("Number"):
            flash(u"Must provide number of shares","error")
            return render_template("sell.html")

        
        symbol = request.form.get("Quote")
        shares = - eval(request.form.get("Number"))

        #if not an integer in shares
        if type(eval(request.form.get("Number"))) != int:
            flash(u"Must provide a number","error")
            return render_template("sell.html")

        #if shares are not there
        crsr.execute("Select shares from portfolio where symbol = '{}' and userId = {}",format(symbol, session["user_id"]))
        current_shares = crsr.fetchall()

        shares_owned = int()


        #if not enough stock
        for i in current_shares:
            for j in i:
                shares_owned = int(j)
                
        if eval(request.form.get("Number")) > shares_owned:
            flash(u"Not enough shares","error")
            return render_template("sell.html")



        # getting latest data in case market is closed (for whatever reason)
        today = datetime.date.today()
        date = today
        strdate = datetime.date.today().strftime("%d-%m-%Y")

        while True:
            try:
                df = get_ohlcv(symbol, strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            # if incorrect symbol given
            except:
                flash(u"Please enter valid symbol","error")
                return render_template("sell.html")
            break
            
        symbolDict = df.to_dict('records')[0]


        #Inserting data in history table
        crsr.execute("INSERT INTO history (Symbol, Shares, Price, Date_Time, UserId) VALUES ('{}',{}, {}, '{}', {})".format(symbol, shares, symbolDict["Close"], datetime.datetime.now(), session["user_id"] ))
        mydb.commit()

        #Inserting data in portfolio
        crsr.execute("Select symbol from portfolio where userID = {}".format(session['user_id']))
        symbols_present = crsr.fetchall()

        existing_symbols = []
        for i in symbols_present:
            for j in i:
                existing_symbols.append(j)

        print(existing_symbols)

        if symbol in existing_symbols:
            crsr.execute("Update Portfolio set shares = shares + {} where userId = {} and symbol = '{}'".format(shares, session['user_id'], symbol))
            mydb.commit()
        
        
        return render_template("sell.html", symbolDict = symbolDict, symbol = symbol, shares = shares)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")


@app.route("/history")
def history():
    """ Show transaction history """
    crsr.execute("SELECT symbol, shares, price, date_time FROM history WHERE userid = {} ORDER BY date_time DESC".format(session["user_id"]))
    rows = crsr.fetchall()

    return render_template("history.html", rows=rows)

@app.route("/portfolio")
@login_required
def portfolio():
    """Show portfolio of stocks"""

    crsr.execute("SELECT cash FROM users WHERE id = {}".format(session["user_id"]))
    rows = crsr.fetchall()
    cash = rows[0][0]

    crsr.execute("SELECT symbol, shares FROM portfolio WHERE userid = {}".format(session["user_id"]))
    rows = crsr.fetchall()

    # getting latest data in case market is closed (for whatever reason)
    today = datetime.date.today()
    date = today
    strdate = datetime.date.today().strftime("%d-%m-%Y")

    costList = []
    priceList = []
    pricetotal = 0

    for row in rows:
        crsr.execute("SELECT SUM(price * shares) FROM history WHERE userid = {} and symbol = '{}'".format(session["user_id"], row[0]))
        cost = crsr.fetchall()
        costList.append(int(cost[0][0]))

        while True:
            try:
                df = get_ohlcv(row[0], strdate)
            except KeyError:
                date = date - datetime.timedelta(days=1)
                strdate = date.strftime("%d-%m-%Y")
                continue
            break
        currentPrice = df.to_dict('records')[0]['Close']
        priceList.append(currentPrice)

        pricetotal = currentPrice * row[1] + pricetotal 

    grandtotal = cash + pricetotal
    grandtotal = inr(grandtotal)
    cash = inr(cash)

    return render_template("portfolio.html", grandtotal = grandtotal, cash = cash, rows = rows, priceList = priceList, costList = costList)


if __name__ == '__main__':
   app.run(debug=True)