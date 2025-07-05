from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CURRENCY_FILE = 'currency.txt'

# Translations
translations = {
    'en': {
        'greeting': 'Hello',
        'balance': 'Your balance:',
        'toggle': 'Show/Hide',
        'transfer': 'Transfer Funds',
        'select_lang': 'Select Language',
        'logout': 'Logout',
        'account_number': 'Account Number',
        'bank_name': 'Bank Name',
        'amount': 'Amount',
        'back': 'Back to Dashboard',
        'upgrade_msg': 'You need to upgrade your account first.'
    },
    'fil': {
        'greeting': 'Kumusta',
        'balance': 'Iyong balanse:',
        'toggle': 'Ipakita/Itago',
        'transfer': 'Maglipat ng Pondo',
        'select_lang': 'Pumili ng Wika',
        'logout': 'Mag-logout',
        'account_number': 'Numero ng Account',
        'bank_name': 'Pangalan ng Bangko',
        'amount': 'Halaga',
        'back': 'Bumalik sa Dashboard',
        'upgrade_msg': 'Kailangan mong i-upgrade ang iyong account muna.'
    },
    'fr': {
        'greeting': 'Bonjour',
        'balance': 'Votre solde :',
        'toggle': 'Afficher/Masquer',
        'transfer': 'Transférer des Fonds',
        'select_lang': 'Choisir la Langue',
        'logout': 'Déconnexion',
        'account_number': 'Numéro de Compte',
        'bank_name': 'Nom de Banque',
        'amount': 'Montant',
        'back': 'Retour au Tableau de Bord',
        'upgrade_msg': "Vous devez d'abord mettre à niveau votre compte."
    }
}

def init_db():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            balance REAL DEFAULT 71000000
        )
    """)
    conn.commit()
    conn.close()

def get_currency():
    if os.path.exists(CURRENCY_FILE):
        with open(CURRENCY_FILE, 'r') as f:
            parts = f.read().strip().split(',')
            return parts[0], parts[1]
    return '₱', 'PHP'

def set_currency(symbol, name):
    with open(CURRENCY_FILE, 'w') as f:
        f.write(f"{symbol},{name}")

init_db()

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists.")
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    language = session.get('language', 'en')
    words = translations.get(language, translations['en'])

    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    balance = result[0] if result else 0
    conn.close()

    symbol, name = get_currency()

    return render_template('dashboard.html', username=username, balance=balance,
                           language=language, words=words, currency_symbol=symbol, name= get_currency, currency_name=get_currency)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' not in session:
        return redirect('/login')

    language = session.get('language', 'en')
    words = translations.get(language, translations['en'])

    message = ''
    if request.method == 'POST':
        message = words['upgrade_msg']

    return render_template('transfer.html', message=message, words=words)

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    session['language'] = language
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                session['role'] = 'admin' if username == 'admin' else 'user'
                return redirect('/dashboard')
        
        flash('Invalid username or password')
        return redirect('/login')
    
    return render_template('login.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin/login')

    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    if request.method == 'POST':
        if 'update_balance' in request.form:
            username = request.form['username']
            new_balance = float(request.form['balance'])
            c.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, username))
            conn.commit()
        elif 'change_currency' in request.form:
            symbol = request.form['symbol']
            name = request.form['name']
            set_currency(symbol, name)

    c.execute("SELECT username, balance FROM users")
    users = c.fetchall()
    conn.close()
    symbol, name = get_currency()

    return render_template('admin_dashboard.html', users=users, currency_symbol=symbol, currency_name=name)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')

if __name__ == '__main__':
    app.run(debug=True)
