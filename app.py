import os
import logging
from flask import Flask, render_template, redirect, url_for, session, request
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
logging.basicConfig(level=logging.INFO)

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['LOCTOGLOB']
users_collection = db['login_users']

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '220701175@rajalakshmi.edu.in')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'eghl xest absr anqv')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/connectDb', methods=['GET', 'POST'])
def connectDb():
    if request.method == 'POST':
        username = request.form.get('signup-username')
        email = request.form.get('signup-email')
        password = request.form.get('signup-password')
        confirm_password = request.form.get('signup-confirm-password')

        if password != confirm_password:
            return render_template('login.html', message='Passwords do not match!')

        user = users_collection.find_one({'email': email})
        if user:
            return render_template('login.html', message='Mail already exists!')

        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': password,
            'verified': False
        })

        user = users_collection.find_one({'username': username})
        verification_link = url_for('verify_email', user_id=str(user['_id']), _external=True)

        msg = Message('Email Verification', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Hi {username},\n\nPlease click the link to verify your email: {verification_link}'
        mail.send(msg)

        return render_template('login.html', message='Signup successful! Please check your email to verify your account.')

    return render_template('login.html')

@app.route('/verify_email/<user_id>')
def verify_email(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if user:
        if user['verified']:
            return render_template('login.html', message='Account already verified. Please log in.')

        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'verified': True}})
        session['username'] = user['username']

        return redirect(url_for('dashboard'))

    return render_template('login.html', message='Invalid verification link.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session: 
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('login-username')
        password = request.form.get('login-password')
        user = users_collection.find_one({'username': username})

        if user and user['password'] == password:
            if not user['verified']:
                return render_template('login.html', message='Please verify your email before logging in.')
            
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    
    return render_template('login.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form.get('reset-email')
        user = users_collection.find_one({'email': email})

        if user:
            # Generate a verification token (can use user's ObjectId or a hash)
            user_id = str(user['_id'])
            verification_link = url_for('reset_verify', user_id=user_id, _external=True)

            # Send email with verification link
            msg = Message('Password Reset Verification', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Hi {user["username"]},\n\nPlease click the link to verify your email and reset your password: {verification_link}'
            mail.send(msg)

            return render_template('login.html', message='A password reset link has been sent to your email. Please verify to proceed.')
        else:
            return render_template('reset.html', message='Email not found. Please try again.')

    return render_template('reset.html')

@app.route('/reset_verify/<user_id>', methods=['GET', 'POST'])
def reset_verify(user_id):
    if request.method == 'POST':
        new_password = request.form.get('reset-password')
        
        # Update the user's password
        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': new_password}})

        return render_template('login.html', message='Password updated successfully! You can now log in.')

    return render_template('reset_verify.html', user_id=user_id)


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

@app.route('/log-out')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
