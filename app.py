from flask import Flask, render_template, request, redirect, session, flash
import json, os

app = Flask(__name__)
app.secret_key = 'secret'

# Translation dictionary
translations = {
    'en': {
        'title': 'Transfer Funds',
        'account_number': 'Account Number',
        'bank': 'Bank Name',
        'amount': 'Amount',
        'confirm': 'Confirm Transfer',
        'back': 'Back to Dashboard',
        'upgrade': 'You need to upgrade your account first.'
    },
    'es': {
        'title': 'Transferir Fondos',
        'account_number': 'Número de Cuenta',
        'bank': 'Banco',
        'amount': 'Cantidad',
        'confirm': 'Confirmar Transferencia',
        'back': 'Volver al Panel',
        'upgrade': 'Necesita actualizar su cuenta primero.'
    },
    'fr': {
        'title': 'Transférer des Fonds',
        'account_number': 'Numéro de Compte',
        'bank': 'Banque',
        'amount': 'Montant',
        'confirm': 'Confirmer le Transfert',
        'back': 'Retour au Tableau de Bord',
        'upgrade': 'Vous devez d’abord mettre à niveau votre compte.'
    }
}

def load_users():
    if not os.path.exists('users.json'):
        return []
    with open('users.json') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

# Currency formatter
def format_currency(amount, symbol):
    if symbol == 'TND':
        return f'TND {amount:,.3f}'
    elif symbol == '$':
        return f'${amount:,.2f}'
    elif symbol == '€':
        return f'€{amount:,.2f}'
    elif symbol == '₱':
        return f'₱{amount:,.2f}'
    else:
        return f'{symbol} {amount:,}'

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
    formatted_balance = format_currency(user['balance'], user['currency'])
    return render_template('dashboard.html', user=user, formatted_balance=formatted_balance)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    user = next((u for u in users if u['username'] == session['user']), None)
    lang = user.get('language', 'en')
    t = translations.get(lang, translations['en'])

    if request.method == 'POST':
        flash(t['upgrade'])
        return redirect('/transfer')

    return render_template('transfer.html', t=t)

@app.route('/set-language', methods=['POST'])
def set_language():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    for u in users:
        if u['username'] == session['user']:
            u['language'] = request.form['language']
            save_users(users)
            break
    return redirect('/dashboard')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or session['user'] != 'admin':
        return redirect('/login')
    
    users = load_users()

    if request.method == 'POST':
        username = request.form['username']
        balance = int(request.form['balance'])
        currency = request.form['currency']
        for u in users:
            if u['username'] == username:
                u['balance'] = balance
                u['currency'] = currency
        save_users(users)
        flash('User info updated.')
        return redirect('/admin')

    return render_template('admin.html', users=users, format_currency=format_currency)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
