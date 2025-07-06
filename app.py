from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
import json

app = Flask(__name__, static_folder='static')
app.secret_key = 'smarterab3611'  

# Create users.json if it doesn't exist
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump([], f)

# Currency formatting helper
def format_currency(amount, symbol):
    try:
        amount = float(amount)
        if symbol == 'TND':
            return f"{symbol} {amount:,.3f}"
        else:
            return f"{symbol}{amount:,.2f}"
    except Exception:
        return f"{symbol}{amount}"

# Supported languages
LANGUAGES = {
    'en': {
        'title': 'Transfer Funds',
        'account_number': 'Account Number',
        'bank': 'Bank',
        'amount': 'Amount',
        'confirm': 'Confirm',
        'upgrade_msg': 'You need to upgrade your account first.'
    },
    'fr': {
        'title': 'Transférer des fonds',
        'account_number': 'Numéro de compte',
        'bank': 'Banque',
        'amount': 'Montant',
        'confirm': 'Confirmer',
        'upgrade_msg': 'Vous devez d\'abord mettre à niveau votre compte.'
    },
    'es': {
        'title': 'Transferir Fondos',
        'account_number': 'Número de Cuenta',
        'bank': 'Banco',
        'amount': 'Cantidad',
        'confirm': 'Confirmar',
        'upgrade_msg': 'Necesita actualizar su cuenta primero.'
    }
}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    with open("users.json", "r") as f:
        users = json.load(f)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if any(u['username'] == username for u in users):
            flash('Username already exists.')
            return redirect('/register')

        users.append({
            "username": username,
            "password": password,
            "balance": 71000000,
            "currency": "₱",
            "language": "en"
        })

        with open("users.json", "w") as f:
            json.dump(users, f)

        flash('Registered successfully.')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    with open("users.json", "r") as f:
        users = json.load(f)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'secret123':
            session['admin'] = True
            return redirect('/admin')

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            session['username'] = user['username']
            session['language'] = user.get('language', 'en')
            return redirect('/dashboard')

        flash('Invalid credentials.')
        return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    language = session.get('language', 'en')

    return render_template('dashboard.html', username=session['username'], lang=LANGUAGES[language])

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' not in session:
        return redirect('/login')

    language = session.get('language', 'en')
    if request.method == 'POST':
        flash(LANGUAGES[language]['upgrade_msg'])
        return redirect('/transfer')

    return render_template('transfer.html', lang=LANGUAGES[language])

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect('/login')

    with open("users.json", "r") as f:
        users = json.load(f)

    if request.method == 'POST':
        username = request.form['username']
        balance = float(request.form['balance'])
        currency = request.form['currency']

        for user in users:
            if user['username'] == username:
                user['balance'] = balance
                user['currency'] = currency

        with open("users.json", "w") as f:
            json.dump(users, f)

        flash("User updated successfully.")
        return redirect('/admin')

    return render_template('admin.html', users=users, format_currency=format_currency)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
