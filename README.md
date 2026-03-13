📦 SmartCartAI

🚀 SmartCartAI is a full-featured e-commerce platform built with FastAPI and PostgreSQL, designed to deliver an Amazon-like shopping experience with Indian localization.

It includes secure authentication, product catalog, shopping cart, order management, email notifications, and analytics.

🎯 Overview

SmartCartAI provides a modern online shopping platform with features such as:

User authentication

Product browsing

Shopping cart

Order management

Email notifications

Secure checkout

Admin statistics

The project follows clean architecture with modular FastAPI routes, SQLAlchemy ORM, and Jinja2 templates.

✨ Features
👤 User Management

User Registration with email verification

Secure Login / Logout using JWT tokens

Password Reset functionality

Profile Management

Address Management (CRUD operations)

🛍️ Shopping Features

Product Catalog with categories

Advanced Search & Filters

Product Details Page

Shopping Cart

Wishlist Management

Order Placement & Tracking

Order History

💳 Payment & Checkout

Multiple Payment Methods

Credit / Debit Card

UPI

Net Banking

Cash on Delivery

Coupon System

Secure Checkout Process

Order Summary with calculations

📧 Email Notifications

Automated emails are sent for:

Welcome Emails

Order Confirmations

Password Reset Emails

Password Change Confirmations

Shipping Updates

Includes professional HTML templates with Indian branding.

🛡️ Security Features

Password hashing using bcrypt

JWT token authentication

HTTP-Only cookies

Secure session management

Input validation with Pydantic

Protection against SQL injection

🛠️ Tech Stack
Backend
Technology	Version	Purpose
Python	3.10+	Core language
FastAPI	0.104.1	Web framework
PostgreSQL	14+	Database
SQLAlchemy	2.0.23	ORM
Pydantic	2.5.0	Data validation
JWT	3.3.0	Authentication
Passlib	1.7.4	Password hashing
Email & Communication
Technology	Purpose
SMTP (Hostinger)	Email sending
Jinja2	Email templates
Python Email Libraries	MIME handling
Frontend
Technology	Purpose
HTML5	Structure
CSS3	Styling
JavaScript	Interactivity
Jinja2	Templating
Font Awesome	Icons


## 📁 Project Structure

```
SmartCartAI/
│
├── routes/                     # API Routes
│   ├── auth.py
│   ├── addresses.py
│   ├── products.py
│   ├── orders.py
│   ├── stats.py
│   └── web.py
│
├── templates/                  # HTML Templates
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── order_detail.html
│   ├── product.html
│   ├── deals.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── reset_password_confirmation.html
│
├── utils/                      # Utility Functions
│   ├── email_utils.py
│   ├── order_utils.py
│   └── security.py
│
├── static/                     # Static Files
│   ├── css/
│   ├── js/
│   └── images/
│
├── main.py                     # Application entry point
├── database.py                 # Database connection setup
├── models.py                   # SQLAlchemy models
├── schemas.py                  # Pydantic schemas
├── crud.py                     # CRUD operations
├── auth.py                     # Authentication logic
├── auth_utils.py               # Authentication helper functions
├── config.py                   # Application configuration
├── data.py                     # Sample product data
├── init_db.py                  # Database initialization
│
├── requirements.txt            # Project dependencies
├── .env                        # Environment variables
└── README.md                   # Project documentation
```

🔧 Installation
Prerequisites

### 🔐 Login & Account Pages
![Login Page](static/images/logincart.png)
![Create Account](static/images/creataccouncart.png)

### 🏠 Dashboard & Navigation
![User Dashboard](static/images/userdashbardcant.png)
![Home Page](static/images/hompagesmartcartai.png)
![Home Page 2](static/images/home1.png)
![All Orders](static/images/allordercart.png)

### 🛒 Shopping & Deals
![Shopping Cart](static/images/shopingcart.png)
![Today's Deals](static/images/todaysdealcart.png)

### 📦 Order Tracking
![Order Tracking](static/images/ordertrackingcart.png)

### 📧 Email Tracking
![Email Tracking 1](static/images/Email- Order Confirmed_page-0001.jpg)
![Email Tracking 2](static/images/Email- Order Confirmed_page-0002.jpg)


Python 3.10+

PostgreSQL 14+

Git

Clone the Repository
git clone https://github.com/RavishankarGavhane/smartcartai.git
cd smartcartai
Create Virtual Environment
python -m venv venv

Activate environment:

Windows

venv\Scripts\activate

Linux / Mac

source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
⚙️ Configuration

Create a .env file in the root directory.

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/smartcartai

# JWT Configuration
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# App Configuration
DEBUG=True
APP_NAME=SmartCartAI
APP_VERSION=2.0.0

# Email Configuration
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=587
SMTP_USER=your-email@yourdomain.com
SMTP_PASS=your-email-password

# Display Settings
DISPLAY_EMAIL=info@yourdomain.com
DISPLAY_NAME=SmartCartAI Support
SUPPORT_EMAIL=support@yourdomain.com
💾 Database Setup
Create PostgreSQL Database
CREATE DATABASE smartcartai;

CREATE USER smartcart_user WITH PASSWORD 'your_password';

GRANT ALL PRIVILEGES ON DATABASE smartcartai TO smartcart_user;
Initialize Database
python init_db.py

This will:

Create all tables

Load sample products

Create indexes

🚀 Running the Application
Development Server
uvicorn main:app --reload

Application URLs:

Web App

http://localhost:8000

API Documentation

http://localhost:8000/docs

Alternative Docs

http://localhost:8000/redoc
🧪 Testing

Test database connection:

python -c "from database import engine; engine.connect()"

Check tables:

python -c "from database import Base; print(Base.metadata.tables.keys())"
🚢 Deployment
Production Checklist

Set DEBUG=False

Use a secure SECRET_KEY

Configure production database

Enable SSL

Configure email services

Enable monitoring & backups

Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
🤝 Contributing

Fork the repository

Create a feature branch

git checkout -b feature/AmazingFeature

Commit changes

git commit -m "Add AmazingFeature"

Push to branch

git push origin feature/AmazingFeature

Open a Pull Request

📄 License

This project is licensed under the MIT License.

📞 Support

For support or questions:

📧 gavhane.ravishankar4@gmail.com