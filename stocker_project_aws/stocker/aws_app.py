import boto3
import hashlib
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# AWS Configuration
AWS_REGION = 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

# DynamoDB Tables
users_table = dynamodb.Table('stocker_users')
trades_table = dynamodb.Table('stocker_trades')
portfolio_table = dynamodb.Table('stocker_portfolio')

# SNS Topic ARN (you'll need to create this in AWS)
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:stocker-notifications'

# Sample stock data (same as local version)
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

def init_aws_tables():
    """Initialize DynamoDB tables if they don't exist"""
    try:
        # Create users table
        users_table = dynamodb.create_table(
            TableName='stocker_users',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'username-index',
                    'KeySchema': [
                        {'AttributeName': 'username', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create trades table
        trades_table = dynamodb.create_table(
            TableName='stocker_trades',
            KeySchema=[
                {'AttributeName': 'trade_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'trade_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Create portfolio table
        portfolio_table = dynamodb.create_table(
            TableName='stocker_portfolio',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'symbol', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'symbol', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        print("Tables created successfully")
        
    except Exception as e:
        print(f"Tables might already exist: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_trade_notification(email, trade_details):
    """Send trade notification via SNS"""
    try:
        message = f"""
        Trade Confirmation - Stocker Platform
        
        Trade Details:
        Action: {trade_details['action'].upper()}
        Symbol: {trade_details['symbol']}
        Quantity: {trade_details['quantity']}
        Price: ${trade_details['price']:.2f}
        Total: ${trade_details['total']:.2f}
        Time: {trade_details['timestamp']}
        
        Thank you for using Stocker!
        """
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"Trade Confirmation - {trade_details['action'].upper()} {trade_details['symbol']}"
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

def get_user_portfolio(user_id):
    """Get user portfolio from DynamoDB"""
    try:
        response = portfolio_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        
        portfolio_value = 0
        portfolio_data = []
        
        for item in response['Items']:
            symbol = item['symbol']
            quantity = int(item['quantity'])
            avg_price = float(item['avg_price'])
            
            if quantity > 0:
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
    
    except Exception as e:
        print(f"Error getting portfolio: {e}")
        return [], 0

# Routes (same as local version with DynamoDB adaptations)
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
        
        try:
            user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            password_hash = hash_password(password)
            
            users_table.put_item(
                Item={
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'password_hash': password_hash,
                    'role': role,
                    'balance': Decimal('10000.0'),
                    'created_at': datetime.now().isoformat()
                },
                ConditionExpression='attribute_not_exists(username)'
            )
            
            flash('Account created successfully! You can now log in.')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash('Username or email already exists!')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)
        
        try:
            response = users_table.query(
                IndexName='username-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(username)
            )
            
            if response['Items'] and response['Items'][0]['password_hash'] == password_hash:
                user = response['Items'][0]
                
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user.get('role', 'trader')
                session['email'] = user['email']
                
                if user.get('role') == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!')
                
        except Exception as e:
            flash('Login failed!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get user balance
        response = users_table.get_item(Key={'user_id': session['user_id']})
        balance = float(response['Item']['balance'])
        
        # Get portfolio value
        _, portfolio_value = get_user_portfolio(session['user_id'])
        
        return render_template('dashboard.html', 
                             stocks=STOCKS, 
                             balance=balance, 
                             portfolio_value=portfolio_value)
    except Exception as e:
        flash('Error loading dashboard!')
        return redirect(url_for('login'))

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
    
    try:
        # Get current user data
        user_response = users_table.get_item(Key={'user_id': session['user_id']})
        user = user_response['Item']
        balance = float(user['balance'])
        
        if action == 'buy':
            if balance < total_cost:
                flash('Insufficient balance!')
                return redirect(url_for('trade', symbol=symbol))
            
            # Update balance
            new_balance = balance - total_cost
            users_table.update_item(
                Key={'user_id': session['user_id']},
                UpdateExpression='SET balance = :balance',
                ExpressionAttributeValues={':balance': Decimal(str(new_balance))}
            )
            
            # Update portfolio
            try:
                portfolio_response = portfolio_table.get_item(
                    Key={'user_id': session['user_id'], 'symbol': symbol}
                )
                
                if 'Item' in portfolio_response:
                    old_quantity = int(portfolio_response['Item']['quantity'])
                    old_avg_price = float(portfolio_response['Item']['avg_price'])
                    new_quantity = old_quantity + quantity
                    new_avg_price = ((old_quantity * old_avg_price) + (quantity * current_price)) / new_quantity
                    
                    portfolio_table.update_item(
                        Key={'user_id': session['user_id'], 'symbol': symbol},
                        UpdateExpression='SET quantity = :qty, avg_price = :price',
                        ExpressionAttributeValues={
                            ':qty': new_quantity,
                            ':price': Decimal(str(new_avg_price))
                        }
                    )
                else:
                    portfolio_table.put_item(
                        Item={
                            'user_id': session['user_id'],
                            'symbol': symbol,
                            'quantity': quantity,
                            'avg_price': Decimal(str(current_price))
                        }
                    )
            except Exception as e:
                print(f"Portfolio update error: {e}")
        
        else:  # sell
            # Check portfolio
            try:
                portfolio_response = portfolio_table.get_item(
                    Key={'user_id': session['user_id'], 'symbol': symbol}
                )
                
                if 'Item' not in portfolio_response or int(portfolio_response['Item']['quantity']) < quantity:
                    flash('Insufficient shares!')
                    return redirect(url_for('trade', symbol=symbol))
                
                # Update balance
                new_balance = balance + total_cost
                users_table.update_item(
                    Key={'user_id': session['user_id']},
                    UpdateExpression='SET balance = :balance',
                    ExpressionAttributeValues={':balance': Decimal(str(new_balance))}
                )
                
                # Update portfolio
                old_quantity = int(portfolio_response['Item']['quantity'])
                new_quantity = old_quantity - quantity
                
                if new_quantity == 0:
                    portfolio_table.delete_item(
                        Key={'user_id': session['user_id'], 'symbol': symbol}
                    )
                else:
                    portfolio_table.update_item(
                        Key={'user_id': session['user_id'], 'symbol': symbol},
                        UpdateExpression='SET quantity = :qty',
                        ExpressionAttributeValues={':qty': new_quantity}
                    )
                    
            except Exception as e:
                flash('Portfolio update failed!')
                return redirect(url_for('trade', symbol=symbol))
        
        # Record trade
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        timestamp = datetime.now().isoformat()
        
        trades_table.put_item(
            Item={
                'trade_id': trade_id,
                'user_id': session['user_id'],
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': Decimal(str(current_price)),
                'total': Decimal(str(total_cost)),
                'timestamp': timestamp
            }
        )
        
        # Send email notification
        trade_details = {
            'action': action,
            'symbol': symbol,
            'quantity': quantity,
            'price': current_price,
            'total': total_cost,
            'timestamp': timestamp
        }
        send_trade_notification(session.get('email', ''), trade_details)
        
        flash(f'Successfully {action} {quantity} shares of {symbol}!')
        
    except Exception as e:
        flash('Trade execution failed!')
        print(f"Trade error: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/portfolio')
def portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    portfolio_data, portfolio_value = get_user_portfolio(session['user_id'])
    
    # Get balance
    try:
        response = users_table.get_item(Key={'user_id': session['user_id']})
        balance = float(response['Item']['balance'])
    except:
        balance = 0
    
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
    
    try:
        response = trades_table.query(
            IndexName='user-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(session['user_id'])
        )
        
        trades = []
        for item in response['Items']:
            trades.append([
                item['symbol'],
                item['action'],
                int(item['quantity']),
                float(item['price']),
                float(item['total']),
                item['timestamp']
            ])
        
        # Sort by timestamp descending
        trades.sort(key=lambda x: x[5], reverse=True)
        
    except Exception as e:
        trades = []
        print(f"Error getting trade history: {e}")
    
    return render_template('history.html', trades=trades)

# Admin routes
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.')
        return redirect(url_for('login'))
    
    try:
        # Get stats from DynamoDB
        # This is simplified - in production you'd use proper aggregation
        users_response = users_table.scan()
        trades_response = trades_table.scan()
        
        total_users = len([u for u in users_response['Items'] if u.get('role') == 'trader'])
        total_trades = len(trades_response['Items'])
        
        total_volume = sum(float(t.get('total', 0)) for t in trades_response['Items'] if t.get('action') == 'buy')
        total_cash = sum(float(u.get('balance', 0)) for u in users_response['Items'])
        
        return render_template('admin_dashboard.html', 
                             total_users=total_users,
                             total_trades=total_trades,
                             total_volume=total_volume,
                             total_cash=total_cash)
    except Exception as e:
        flash('Error loading admin dashboard!')
        return redirect(url_for('login'))

# Additional admin routes would follow similar patterns...

@app.route('/api/stocks')
def api_stocks():
    # Simulate price changes (same as local version)
    for symbol in STOCKS:
        change_percent = random.uniform(-0.02, 0.02)
        STOCKS[symbol]['price'] *= (1 + change_percent)
        STOCKS[symbol]['change'] = STOCKS[symbol]['price'] * change_percent
        STOCKS[symbol]['price'] = round(STOCKS[symbol]['price'], 2)
        STOCKS[symbol]['change'] = round(STOCKS[symbol]['change'], 2)
    
    return jsonify(STOCKS)

if __name__ == '__main__':
    init_aws_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)