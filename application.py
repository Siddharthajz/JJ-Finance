from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
import datetime

from helpers import plot_data, get_ohlcv
from news import get_links, get_titles

#GET - when link is pressed or button or anything is pressed
#POST - when you commit some information to that website


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
    

@app.route("/watchlist", methods=['GET', 'POST'])
def watchlist():
    return render_template("watchlist.html")


@app.route("/news")
def news():
    return render_template('news.html')

    
@app.route("/currency")
def currency():
    return render_template('currency.html')
    



if __name__ == '__main__':
   app.run(debug=True)