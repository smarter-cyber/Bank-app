from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for sessions

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not os.path.exists('users.json'):
            flash("No users found.")
            return redirect(url_for('register'))

        with open('users.json', 'r') as f:
            try:
                users = json.load(f)
            except:
                users = []

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not os.path.exists('users.json'):
            users = []
        else:
            with open('users.json', 'r') as f:
                try:
                    users = json.load(f)
                except:
                    users = []

        if any(u['username'] == username for u in users):
            flash('Username already exists.')
            return redirect(url_for('register'))

        users.append({'username': username, 'password': password, 'balance': 71000000})

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']

    with open('users.json', 'r') as f:
        users = json.load(f)
        user = next((u for u in users if u['username'] == username), None)

    if not user:
        flash("User not found.")
        return redirect(url_for('login'))

    return f"Welcome {username}! Balance: {user['balance']}"

if __name__ == '__main__':
    app.run(debug=True)
