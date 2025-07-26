import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Sample stock data with realistic prices
STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'price': 185.50, 'change': 2.75},
    'GOOGL': {'name': 'Alphabet Inc.', 'price': 142.30, 'change': -1.20},
    'MSFT': {'name': 'Microsoft Corp.', 'price': 378.85, 'change': 4.60},
    'AMZN': {'name': 'Amazon.com Inc.', 'price': 145.75, 'change': -2.85},
    'TSLA': {'name': 'Tesla Inc.', 'price': 248.42, 'change': 8.90},
    'META': {'name': 'Meta Platforms', 'price': 325.60, 'change': 5.25},
    'NVDA': {'name': 'NVIDIA Corp.', 'price': 875.30, 'change': 12.40},
    'NFLX': {'name': 'Netflix Inc.', 'price': 445.20, 'change': -3.75},
    'ADBE': {'name': 'Adobe Inc.', 'price': 485.90, 'change': 6.80},
    'CRM': {'name': 'Salesforce Inc.', 'price': 215.40, 'change': -1.95},
    'ORCL': {'name': 'Oracle Corp.', 'price': 102.85, 'change': 1.30},
    'IBM': {'name': 'IBM', 'price': 158.75, 'change': 0.85},
    'INTC': {'name': 'Intel Corp.', 'price': 43.20, 'change': -0.60},
    'AMD': {'name': 'AMD Inc.', 'price': 142.60, 'change': 3.45},
    'UBER': {'name': 'Uber Technologies', 'price': 65.40, 'change': 2.10},
    'LYFT': {'name': 'Lyft Inc.', 'price': 14.85, 'change': -0.35},
    'SPOT': {'name': 'Spotify Technology', 'price': 185.20, 'change': 4.20},
    'ZOOM': {'name': 'Zoom Video', 'price': 68.90, 'change': -1.15},
    'SQ': {'name': 'Block Inc.', 'price': 78.35, 'change': 2.80},
    'PYPL': {'name': 'PayPal Holdings', 'price': 62.45, 'change': -0.95},
    'V': {'name': 'Visa Inc.', 'price': 245.70, 'change': 1.85},
    'MA': {'name': 'Mastercard Inc.', 'price': 385.20, 'change': 3.60},
    'JPM': {'name': 'JPMorgan Chase', 'price': 158.90, 'change': 2.25},
    'GS': {'name': 'Goldman Sachs', 'price': 365.80, 'change': -1.40},
    'WMT': {'name': 'Walmart Inc.', 'price': 158.25, 'change': 0.75},
    'HD': {'name': 'Home Depot', 'price': 345.60, 'change': 4.15},
    'PG': {'name': 'Procter & Gamble', 'price': 155.30, 'change': 0.90}
}

def init_db():
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'trader',
            balance REAL DEFAULT 10000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, symbol)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_portfolio(user_id):
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT symbol, quantity, avg_price FROM portfolio 
        WHERE user_id = ? AND quantity > 0
    ''', (user_id,))
    portfolio = cursor.fetchall()
    conn.close()
    
    portfolio_value = 0
    portfolio_data = []
    for symbol, quantity, avg_price in portfolio:
        current_price = STOCKS.get(symbol, {}).get('price', 0)
        total_value = quantity * current_price
        gain_loss = (current_price - avg_price) * quantity
        portfolio_value += total_value
        
        portfolio_data.append({
            'symbol': symbol,
            'name': STOCKS.get(symbol, {}).get('name', symbol),
            'quantity': quantity,
            'avg_price': avg_price,
            'current_price': current_price,
            'total_value': total_value,
            'gain_loss': gain_loss
        })
    
    return portfolio_data, portfolio_value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'trader')
        
        conn = sqlite3.connect('stocker.db')
        cursor = conn.cursor()
        
        try:
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            conn.commit()
            flash('Account created successfully! You can now log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!')
        finally:
            conn.close()
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)
        
        conn = sqlite3.connect('stocker.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, role FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            
            if user[2] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user balance
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],))
    balance = cursor.fetchone()[0]
    conn.close()
    
    # Get portfolio value
    _, portfolio_value = get_user_portfolio(session['user_id'])
    
    return render_template('dashboard.html', 
                         stocks=STOCKS, 
                         balance=balance, 
                         portfolio_value=portfolio_value)

@app.route('/trade/<symbol>')
def trade(symbol):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if symbol not in STOCKS:
        flash('Invalid stock symbol!')
        return redirect(url_for('dashboard'))
    
    stock = STOCKS[symbol]
    stock['symbol'] = symbol
    
    return render_template('trade.html', stock=stock)

@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    symbol = request.form['symbol']
    action = request.form['action']
    quantity = int(request.form['quantity'])
    
    if symbol not in STOCKS:
        flash('Invalid stock symbol!')
        return redirect(url_for('dashboard'))
    
    current_price = STOCKS[symbol]['price']
    total_cost = quantity * current_price
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    try:
        # Get current balance
        cursor.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],))
        balance = cursor.fetchone()[0]
        
        if action == 'buy':
            if balance < total_cost:
                flash('Insufficient balance!')
                return redirect(url_for('trade', symbol=symbol))
            
            # Update balance
            new_balance = balance - total_cost
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', 
                         (new_balance, session['user_id']))
            
            # Update portfolio
            cursor.execute('''
                SELECT quantity, avg_price FROM portfolio 
                WHERE user_id = ? AND symbol = ?
            ''', (session['user_id'], symbol))
            existing = cursor.fetchone()
            
            if existing:
                old_quantity, old_avg_price = existing
                new_quantity = old_quantity + quantity
                new_avg_price = ((old_quantity * old_avg_price) + (quantity * current_price)) / new_quantity
                cursor.execute('''
                    UPDATE portfolio SET quantity = ?, avg_price = ?
                    WHERE user_id = ? AND symbol = ?
                ''', (new_quantity, new_avg_price, session['user_id'], symbol))
            else:
                cursor.execute('''
                    INSERT INTO portfolio (user_id, symbol, quantity, avg_price)
                    VALUES (?, ?, ?, ?)
                ''', (session['user_id'], symbol, quantity, current_price))
        
        else:  # sell
            # Check if user has enough shares
            cursor.execute('''
                SELECT quantity FROM portfolio 
                WHERE user_id = ? AND symbol = ?
            ''', (session['user_id'], symbol))
            existing = cursor.fetchone()
            
            if not existing or existing[0] < quantity:
                flash('Insufficient shares!')
                return redirect(url_for('trade', symbol=symbol))
            
            # Update balance
            new_balance = balance + total_cost
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', 
                         (new_balance, session['user_id']))
            
            # Update portfolio
            new_quantity = existing[0] - quantity
            if new_quantity == 0:
                cursor.execute('''
                    DELETE FROM portfolio WHERE user_id = ? AND symbol = ?
                ''', (session['user_id'], symbol))
            else:
                cursor.execute('''
                    UPDATE portfolio SET quantity = ?
                    WHERE user_id = ? AND symbol = ?
                ''', (new_quantity, session['user_id'], symbol))
        
        # Record trade
        cursor.execute('''
            INSERT INTO trades (user_id, symbol, action, quantity, price, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], symbol, action, quantity, current_price, total_cost))
        
        conn.commit()
        flash(f'Successfully {action} {quantity} shares of {symbol}!')
        
    except Exception as e:
        conn.rollback()
        flash('Trade execution failed!')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/portfolio')
def portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    portfolio_data, portfolio_value = get_user_portfolio(session['user_id'])
    
    # Get balance
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],))
    balance = cursor.fetchone()[0]
    conn.close()
    
    total_value = balance + portfolio_value
    
    return render_template('portfolio.html', 
                         portfolio=portfolio_data,
                         balance=balance,
                         portfolio_value=portfolio_value,
                         total_value=total_value)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT symbol, action, quantity, price, total, timestamp
        FROM trades WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (session['user_id'],))
    trades = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', trades=trades)

# Admin routes
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "trader"')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(total) FROM trades WHERE action = "buy"')
    total_volume = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(balance) FROM users')
    total_cash = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_trades=total_trades,
                         total_volume=total_volume,
                         total_cash=total_cash)

@app.route('/admin/portfolio')
def admin_portfolio():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, p.symbol, p.quantity, p.avg_price, u.balance
        FROM portfolio p
        JOIN users u ON p.user_id = u.id
        WHERE p.quantity > 0
        ORDER BY u.username, p.symbol
    ''')
    portfolios = cursor.fetchall()
    conn.close()
    
    return render_template('admin_portfolio.html', portfolios=portfolios, stocks=STOCKS)

@app.route('/admin/history')
def admin_history():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, t.symbol, t.action, t.quantity, t.price, t.total, t.timestamp
        FROM trades t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.timestamp DESC
        LIMIT 100
    ''')
    trades = cursor.fetchall()
    conn.close()
    
    return render_template('admin_history.html', trades=trades)

@app.route('/admin/manage')
def admin_manage():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, balance, role, created_at
        FROM users
        ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_manage.html', users=users)

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('stocker.db')
    cursor = conn.cursor()
    
    try:
        # Delete user's portfolio
        cursor.execute('DELETE FROM portfolio WHERE user_id = ?', (user_id,))
        # Delete user's trades
        cursor.execute('DELETE FROM trades WHERE user_id = ?', (user_id,))
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/users/<int:user_id>/suspend', methods=['POST'])
def suspend_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # This would implement user suspension logic
    # For now, just return success
    return jsonify({'success': True})

# API routes for live updates
@app.route('/api/stocks')
def api_stocks():
    # Simulate price changes
    for symbol in STOCKS:
        change_percent = random.uniform(-0.02, 0.02)  # -2% to +2%
        STOCKS[symbol]['price'] *= (1 + change_percent)
        STOCKS[symbol]['change'] = STOCKS[symbol]['price'] * change_percent
        STOCKS[symbol]['price'] = round(STOCKS[symbol]['price'], 2)
        STOCKS[symbol]['change'] = round(STOCKS[symbol]['change'], 2)
    
    return jsonify(STOCKS)

@app.route('/api/portfolio/<int:user_id>')
def api_portfolio(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Users can only access their own portfolio, admins can access any
    if session.get('role') != 'admin' and session['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    portfolio_data, portfolio_value = get_user_portfolio(user_id)
    return jsonify({
        'portfolio': portfolio_data,
        'portfolio_value': portfolio_value
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)