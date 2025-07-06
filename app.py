
from flask import Flask, render_template, request, redirect, session, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load user data
def load_users():
    if not os.path.exists('users.json'):
        return []
    with open('users.json', 'r') as f:
        return json.load(f)

# Save user data
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                session['role'] = 'admin' if username == 'admin' else 'user'
                return redirect('/dashboard')
        flash('Invalid username or password')
        return redirect('/login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username:
                flash('Username already exists')
                return redirect('/register')
        users.append({
            'username': username,
            'password': password,
            'balance': 1000000,
            'currency': '₱',
            'language': 'en'
        })
        save_users(users)
        flash('Account created. Please log in.')
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    user = next((u for u in users if u['username'] == session['user']), None)
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
