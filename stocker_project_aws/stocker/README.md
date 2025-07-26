# Stocker - Professional Stock Trading Platform

A comprehensive stock trading web platform with separate user and admin experiences, supporting both local SQLite and AWS cloud deployments.

![Stocker Platform](https://images.pexels.com/photos/6801648/pexels-photo-6801648.jpeg?auto=compress&cs=tinysrgb&w=1200&h=400&fit=crop)

## 🚀 Features

### 👤 User Features
- **Secure Authentication**: User signup/login with hashed passwords
- **Real-time Trading**: Live stock prices with instant trade execution
- **Portfolio Management**: Comprehensive portfolio tracking and analytics
- **Trade History**: Complete transaction history with detailed records
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Email Notifications**: Trade confirmations via SNS (AWS deployment)

### 🛠️ Admin Features
- **Admin Dashboard**: Platform overview with key statistics
- **User Management**: View and manage all user accounts
- **Portfolio Oversight**: Monitor all user portfolios and holdings
- **Trade Monitoring**: Complete visibility into all platform trades
- **System Controls**: Administrative tools for platform management

### 📊 Stock Market
- **25+ Popular Stocks**: Including AAPL, GOOGL, MSFT, AMZN, TSLA, and more
- **Real-time Updates**: Live price updates every 5 seconds
- **Market Simulation**: Realistic price movements and trading scenarios

## 🏗️ Architecture

### Local Deployment
- **Backend**: Flask web framework
- **Database**: SQLite for data persistence
- **Frontend**: Jinja2 templates with vanilla JavaScript
- **Styling**: Custom CSS with dark theme

### AWS Cloud Deployment
- **Hosting**: EC2 instances
- **Database**: DynamoDB for scalable data storage
- **Notifications**: SNS for email alerts
- **Security**: IAM roles and policies

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3
- boto3 (for AWS deployment)
- Modern web browser

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd stocker
   pip install -r requirements.txt
   ```

2. **Run Local Version**
   ```bash
   python app.py
   ```

3. **Access Platform**
   - Open http://localhost:5000
   - Admin login: `admin` / `admin123`
   - Create new user account for trading

### AWS Deployment

1. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and region
   ```

2. **Setup DynamoDB Tables**
   ```bash
   python aws_app.py
   # Tables will be created automatically on first run
   ```

3. **Configure SNS (Optional)**
   - Create SNS topic in AWS Console
   - Update `SNS_TOPIC_ARN` in `aws_app.py`
   - Subscribe email addresses to the topic

4. **Deploy to EC2**
   ```bash
   # Upload files to EC2 instance
   # Install dependencies
   pip install -r requirements.txt
   # Run application
   python aws_app.py
   ```

## 📁 Project Structure

```
stocker/
├── app.py                     # Local SQLite version
├── aws_app.py                 # AWS DynamoDB version
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── stocker.db                 # Auto-created SQLite database
│
├── static/
│   ├── styles.css             # Dark theme styling
│   └── script.js              # Frontend JavaScript
│
└── templates/
    ├── index.html             # Landing page
    ├── login.html             # User authentication
    ├── signup.html            # User registration
    ├── dashboard.html         # Trading dashboard
    ├── trade.html             # Buy/sell interface
    ├── portfolio.html         # Portfolio management
    ├── history.html           # Trade history
    ├── admin_dashboard.html   # Admin overview
    ├── admin_portfolio.html   # All portfolios view
    ├── admin_history.html     # All trades view
    └── admin_manage.html      # User management
```

## 🎯 Default Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Balance**: $100,000
- **Permissions**: Full platform access

### New User Accounts
- **Starting Balance**: $10,000
- **Permissions**: Trading and portfolio management

## 📈 Available Stocks

The platform includes 27 popular stocks with real-time price simulation:

**Technology**: AAPL, GOOGL, MSFT, AMZN, META, NVDA, ADBE, CRM, ORCL, IBM, INTC, AMD
**Transportation**: UBER, LYFT, TSLA
**Entertainment**: NFLX, SPOT, ZOOM
**Finance**: SQ, PYPL, V, MA, JPM, GS
**Retail**: WMT, HD, PG

## 🔧 Configuration

### Environment Variables (AWS)
```bash
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR-ACCOUNT-ID:stocker-notifications
```

### Database Configuration
- **Local**: SQLite database auto-created as `stocker.db`
- **AWS**: DynamoDB tables created automatically:
  - `stocker_users`
  - `stocker_trades`
  - `stocker_portfolio`

## 🛡️ Security Features

- **Password Hashing**: SHA-256 encryption for all passwords
- **Session Management**: Secure Flask sessions
- **Input Validation**: Server-side validation for all forms
- **SQL Injection Protection**: Parameterized queries
- **Admin Access Control**: Role-based permissions

## 🎨 Design Features

- **Dark Theme**: Professional dark color scheme
- **Responsive Layout**: Mobile-first design approach
- **Live Updates**: Real-time price and portfolio updates
- **Smooth Animations**: Subtle transitions and hover effects
- **Accessibility**: High contrast ratios and keyboard navigation

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔄 API Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /login` - Login form
- `GET /signup` - Registration form
- `POST /login` - User authentication
- `POST /signup` - User registration

### User Routes (Authentication Required)
- `GET /dashboard` - Trading dashboard
- `GET /portfolio` - Portfolio view
- `GET /history` - Trade history
- `GET /trade/<symbol>` - Trading interface
- `POST /execute_trade` - Execute buy/sell orders

### Admin Routes (Admin Authentication Required)
- `GET /admin/dashboard` - Admin overview
- `GET /admin/portfolio` - All portfolios
- `GET /admin/history` - All trades
- `GET /admin/manage` - User management

### API Routes
- `GET /api/stocks` - Live stock prices
- `GET /api/portfolio/<user_id>` - User portfolio data

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # For local deployment
   rm stocker.db
   python app.py
   ```

2. **AWS Permissions Error**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   ```

3. **Port Already in Use**
   ```bash
   # Kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration documentation

## 🔮 Future Enhancements

- Real-time market data integration
- Advanced charting and technical analysis
- Options and futures trading
- Mobile application
- Advanced portfolio analytics
- Social trading features
- API for third-party integrations

---

**Built with ❤️ using Flask, SQLite/DynamoDB, and modern web technologies**