from flask import Flask, render_template, request, redirect, session, flash
import json, os

app = Flask(__name__)
app.secret_key = 'secret'

def load_users():
    if not os.path.exists('users.json'):
        return []
    with open('users.json') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        users = load_users()
        for u in users:
            if u['username'] == uname and u['password'] == pwd:
                session['user'] = uname
                session['role'] = 'admin' if uname == 'admin' else 'user'
                return redirect('/dashboard')
        flash('Invalid credentials')
        return redirect('/login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        users = load_users()
        if any(u['username'] == uname for u in users):
            flash('User exists')
            return redirect('/register')
        users.append({
            'username': uname,
            'password': pwd,
            'balance': 71000000,
            'currency': '₱',
            'language': 'en'
        })
        save_users(users)
        flash('Registered. Please login.')
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
    app.run()
