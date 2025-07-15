from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os

def load_translations():
    with open("translations.json", "r", encoding="utf-8") as f:
        return json.load(f)

def translate(text, lang="en"):
    translations = load_translations()
    return translations.get(text, {}).get(lang, text)

app = Flask(__name__, static_folder='static')
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # Admin login check
        if username == 'admin' and password == 'secret123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        if not os.path.exists('users.json'):
            flash("No users registered yet.")
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
            flash("Invalid username or password.")
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

        users.append({'username': username, 'password': password, 'balance': 71000000, 'currency': '₱'})

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    lang = session.get('lang', 'en')

    with open('users.json', 'r') as f:
        users = json.load(f)
        user = next((u for u in users if u['username'] == username), None)

    if not user:
        flash("User not found.")
        return redirect(url_for('login'))

    currency_symbol = user.get('currency', '₱')

    return render_template('dashboard.html',
                           username=username,
                           balance=user['balance'],
                           currency_symbol=currency_symbol,
                           lang=lang,
                           t=translate)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))

    lang = session.get('lang', 'en')
    message = None

    if request.method == 'POST':
        message = translate("You need to upgrade your account first.", lang)

    return render_template('transfer.html', message=message, lang=lang, t=translate)

@app.route('/set_language', methods=['POST'])
def set_language():
    selected_lang = request.form.get("language", "en")
    session['lang'] = selected_lang
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    with open('users.json', 'r') as f:
        users = json.load(f)

    if request.method == 'POST':
        username = request.form['username']
        new_balance = request.form['balance']
        new_currency = request.form['currency']

        for user in users:
            if user['username'] == username:
                user['balance'] = int(new_balance)
                user['currency'] = new_currency

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        flash("User updated successfully.")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
