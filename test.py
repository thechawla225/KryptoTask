from flask import Flask, request, jsonify, make_response, render_template, session
from datetime import datetime, timedelta
import jwt
from functools import wraps
import sqlite3
from sqlite3 import Error
import time
from multiprocessing import Process, Value
from urllib.request import urlopen
import json


app = Flask(__name__)

# Adding a Secret generated using secrets.token_hex(12)
app.config['SECRET_KEY'] = '5667749b5ec55f17d75f4391'

# Create databse file
connector = sqlite3.connect('alerts.db', check_same_thread=False)

# Set the url
url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"


def create_table(conn, createTableSql):
    # Function to create table
    try:
        c = conn.cursor()
        c.execute(createTableSql)
    except:
        print("Looks like there was an error in creating database")


def lookForPrices(loop_on):
    while True:
        coins = {}
        with open("file.txt") as f:
            for line in f:
                arr = line.split()
                for j in range(0, len(arr), 2):
                    key = arr[j]
                    val = arr[j+1]
                    coins[key] = int(val)
        if loop_on.value == True:
            responses = json.loads(urlopen(url).read())
            print(responses[0])
            print(coins)
            for data in responses:
                if(data['id'] in coins):
                    print(data['id'] + "found in cons")
                    for price in coins[data['id']]:
                        if(price == data['current_price']):
                            sendEmail()
            time.sleep(10)


def sendEmail():
    print("********Email sent******")


def tokenNeeded(func):
    @ wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if(not token):
            return jsonify({'Alert!': 'No Token'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert!': 'Token Invalid!'})
    return decorated


@ app.route('/')
def homePage():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'You are Logged in!'


@ app.route('/login', methods=['POST'])
def loginUser():
    if(request.form['name'] and request.form['password'] == 'ankit'):
        session['loggedIn'] = True
        session['name'] = request.form['name']
        session['coins'] = '{"a":4}'
        # Expiry added to terminate the jwt token later
        token = jwt.encode({'name': request.form['name'], 'expires': str(
            datetime.utcnow() + timedelta(300))}, app.config['SECRET_KEY'])
        return make_response('Logged in!')
        # return jsonify({'token': jwt.decode(token, options={"verify_signature": False})})
    else:
        return make_response("OOPS! Looks like we can't log you in")


@ app.route('/logout', methods=['POST'])
def logOut():
    if(session['loggedIn']):
        session['loggedIn'] = False
        return 'You have been logged out successfully'
    return 'You are logged Out'


@ app.route('/createAlert')
def createAlertShow():
    if(session['loggedIn']):
        return render_template('create.html')
    return render_template('login.html')


@ app.route('/alerts/create', methods=['POST'])
def createAlert():
    coins = {}
    with open("file.txt") as f:
        for line in f:
            arr = line.split()
            for j in range(0, len(arr), 2):
                key = arr[j]
                val = arr[j+1]
                coins[key] = int(val)
    if(session['loggedIn']):
        if(request.form['coinname'] and request.form['alertmeat']):
            alertSQL = """INSERT INTO alerts (names, coinName, alertVal) VALUES ( ?, ?, ?)"""
            params = (
                session['name'], request.form['coinname'], request.form['alertmeat'])
            try:
                connector.execute(alertSQL, params)
                # If that price is not already in  coins dictionary, add it for that coin name
                if(request.form['coinname'] in coins and request.form['alertmeat'] not in coins[request.form['coinname']]):
                    coins[request.form['coinname']].append(
                        request.form['alertmeat'])
                else:
                    coins[request.form['coinname']] = []
                    coins[request.form['coinname']].append(
                        request.form['alertmeat'])
                val1 = " "
                for key, val in coins.items():
                    val1 += key + str(val)
                with open("file.txt", "w") as out_f:
                    out_f.write(val1 + ' ')
                return "Alert Created"
            except Error as e:
                print(e)
        return "Please enter all details correctly"
    else:
        render_template('login.html')


@ app.route('/deleteAlert')
def deleteAlertShow():
    if(session['loggedIn']):
        return render_template('delete.html')
    return render_template('login.html')


@ app.route('/alerts/delete', methods=['POST'])
def deleteAlert():
    if(session['loggedIn']):
        if(request.form['coinname']):
            alertSQL = """DELETE FROM alerts WHERE names = ? and coinName = ? """
            params = (session['name'], request.form['coinname'])

            try:
                connector.execute(alertSQL, params)
                return "Alert Deleted"
            except Error as e:
                print(e)
        else:
            return "Please enter all details correctly"
    else:
        render_template('login.html')
    return render_template('login.html')


if __name__ == '__main__':
    # creating table
    createTableSql = """CREATE TABLE IF NOT EXISTS alerts (
	id AUTO_INCREMENT integer PRIMARY KEY ,
	names VARCHAR(50) NOT NULL,
    coinName VARCHAR(50) NOT NULL,
	alertVal integer NOT NULL);"""
    create_table(connector, createTableSql)
    # Start querying the coin prices
    start = Value('b', True)
    p = Process(target=lookForPrices, args=(start,))
    p.start()
    app.run(debug=True, use_reloader=False)
    p.join()
