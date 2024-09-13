import os
import logging
from flask import Flask, send_from_directory, render_template, jsonify, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Set up logging
logging.basicConfig(level=logging.INFO)

EXECUTABLES_FOLDER = os.path.join(os.getcwd(), 'executables')

if not os.path.exists(EXECUTABLES_FOLDER):
    os.makedirs(EXECUTABLES_FOLDER)

# MongoDB Atlas connection
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['login']
users_collection = db['users']

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})
        if user:
            return 'Username already exists!'

        # Store the password in plain text (Not secure, for testing only)
        users_collection.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/connectDb', methods=['GET', 'POST'])
def connectDb():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})
        if user:
            return 'Username already exists!'

        # Store the password in plain text (Not secure, for testing only)
        users_collection.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))  # Redirect to login page instead of rendering it
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})

        # Direct comparison of the plain text password
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials. Please try again.'
    
    return render_template('login.html')  # Render login page for GET request

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    return render_template('index.html')

@app.route('/serveo')
def serveo():
    return render_template('serveo.html')

@app.route('/ngrok')
def ngrok():
    return render_template('ngrok.html')

if __name__ == '__main__':
    app.run(debug=True)
