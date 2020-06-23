from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

from helpers import plot_data, get_ohlcv
from news import get_links, get_titles

# Configure application
app = Flask(__name__)

app.secret_key = 'super secret key'

# Configure SQL
mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="jjfinance")
crsr=mydb.cursor()

@app.route("/")
def home():
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
            flash(u"must provide password","error")
            return render_template("signup.html")

        # ensure passconfirm was submitted
        elif not request.form.get("confirmation"):
            flash(u"must confirm password","error")
            return render_template("signup.html")

        # ensure password and passconfirm are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            flash(u"passwords do not match","error")
            return render_template("signup.html")

        # hash password
        hashpass = generate_password_hash(request.form.get("password"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect("/")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup.html")



if __name__ == '__main__':
   app.run(debug=True)