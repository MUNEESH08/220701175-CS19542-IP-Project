import os
import logging
from flask import Flask, send_from_directory, render_template, jsonify, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
logging.basicConfig(level=logging.INFO)
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['login']
users_collection = db['users']

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/connectDb', methods=['GET', 'POST'])
def connectDb():
    if request.method == 'POST':
        username = request.form.get('signup-username')
        email = request.form.get('signup-email')  # Added email field
        password = request.form.get('signup-password')
        confirm_password = request.form.get('signup-confirm-password')

        if password != confirm_password:
            return render_template('login.html', message='Passwords do not match!')

        user = users_collection.find_one({'username': username})
        if user:
            return render_template('login.html', message='Username already exists!')

        users_collection.insert_one({'username': username, 'email': email, 'password': password})
        return render_template('login.html', message='Signup successful! Please login.')

    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login-username')
        password = request.form.get('login-password')
        user = users_collection.find_one({'username': username})

        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    
    return render_template('login.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form.get('reset-email')
        new_password = request.form.get('reset-password')
        user = users_collection.find_one({'email': email})

        if user:
            users_collection.update_one({'email': email}, {'$set': {'password': new_password}})
            return render_template('login.html', message='Password updated successfully!')
        else:
            return render_template('reset.html', message='Email not found. Please try again.')

    return render_template('reset.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/serveo')
def serveo():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('serveo.html')

@app.route('/ngrok')
def ngrok():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('ngrok.html')

if __name__ == '__main__':
    app.run(debug=True)
