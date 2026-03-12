# C:\Users\Sonam Gavhane\OneDrive\Desktop\SmartCartAI\utils\email_utils.py

import smtplib
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging to show INFO messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# All configuration from .env file
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
DISPLAY_EMAIL = os.getenv("DISPLAY_EMAIL", "info@keepactivepro.com")
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "SmartCartAI Support")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@keepactivepro.com")
APP_NAME = os.getenv("APP_NAME", "SmartCartAI")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Get domain from email
DOMAIN = DISPLAY_EMAIL.split('@')[1] if '@' in DISPLAY_EMAIL else "keepactivepro.com"


class EmailBaseTemplate:
    """Base template for all emails with consistent header and footer"""
    
    @staticmethod
    def get_base_html(content_html: str, preview_text: str = "") -> str:
        """Wrap content with professional header and footer"""
        current_year = datetime.now().year
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="color-scheme" content="light">
            <meta name="supported-color-schemes" content="light">
            <title>{APP_NAME}</title>
            <style>
                /* Reset styles */
                body, table, td, p, a {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.5;
                }}
                
                body {{
                    background-color: #e3e6e6;
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                }}
                
                /* Container */
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                /* Header */
                .email-header {{
                    background: linear-gradient(135deg, #131921 0%, #232f3e 100%);
                    padding: 30px 20px;
                    text-align: center;
                }}
                
                .logo {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #ff9900;
                    margin-bottom: 5px;
                }}
                
                .logo i {{
                    font-size: 32px;
                    color: #ff9900;
                    margin-right: 5px;
                }}
                
                .domain-badge {{
                    display: inline-block;
                    background: rgba(255,255,255,0.1);
                    color: #ff9900;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    margin-top: 10px;
                }}
                
                /* Content */
                .email-content {{
                    padding: 40px 30px;
                    background-color: #ffffff;
                }}
                
                /* Buttons */
                .btn {{
                    display: inline-block;
                    padding: 14px 30px;
                    background: #ff9900;
                    color: #232f3e !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    margin: 20px 0;
                    border: 1px solid #f7ca00;
                    transition: all 0.2s;
                }}
                
                .btn:hover {{
                    background: #f7ca00;
                    transform: scale(1.02);
                }}
                
                .btn-secondary {{
                    background: #f0f2f2;
                    color: #232f3e !important;
                    border: 1px solid #ddd;
                }}
                
                /* Order Summary Table */
                .order-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: #f8f9fa;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                
                .order-table th {{
                    background: #232f3e;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                }}
                
                .order-table td {{
                    padding: 15px 12px;
                    border-bottom: 1px solid #e7e7e7;
                    font-size: 14px;
                }}
                
                .order-table tr:last-child td {{
                    border-bottom: none;
                }}
                
                /* Price styling */
                .price {{
                    color: #b12704;
                    font-weight: 600;
                }}
                
                .discount {{
                    color: #28a745;
                    font-weight: 600;
                }}
                
                /* Address box */
                .address-box {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #ff9900;
                }}
                
                /* Info box */
                .info-box {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                
                /* Feature grid */
                .feature-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin: 25px 0;
                }}
                
                .feature-item {{
                    text-align: center;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    border: 1px solid #e7e7e7;
                }}
                
                .feature-icon {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                
                .feature-title {{
                    color: #232f3e;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                
                .feature-desc {{
                    color: #666;
                    font-size: 12px;
                }}
                
                /* Security badge */
                .security-badge {{
                    display: inline-block;
                    background: #e8f5e8;
                    color: #28a745;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 13px;
                    margin: 10px 0;
                }}
                
                /* Footer */
                .email-footer {{
                    background: #232f3e;
                    padding: 30px 20px;
                    text-align: center;
                    color: #999;
                }}
                
                .footer-links {{
                    margin-bottom: 15px;
                }}
                
                .footer-links a {{
                    color: #ff9900;
                    text-decoration: none;
                    margin: 0 10px;
                    font-size: 13px;
                }}
                
                .footer-links a:hover {{
                    text-decoration: underline;
                }}
                
                .copyright {{
                    font-size: 12px;
                    color: #666;
                    margin-top: 15px;
                }}
                
                .india-flag {{
                    display: inline-block;
                    width: 18px;
                    height: 12px;
                    background: linear-gradient(135deg, #ff9933 33%, #ffffff 33%, #ffffff 66%, #138808 66%);
                    border-radius: 2px;
                    margin-right: 5px;
                    vertical-align: middle;
                }}
                
                /* Status badges */
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                
                .status-confirmed {{
                    background: #e3f2fd;
                    color: #1976d2;
                }}
                
                .status-shipped {{
                    background: #fff3e0;
                    color: #f57c00;
                }}
                
                .status-delivered {{
                    background: #e8f5e8;
                    color: #388e3c;
                }}
                
                /* Warning box */
                .warning-box {{
                    background: #fff3cd;
                    color: #856404;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 20px 0;
                    border-left: 4px solid #ffc107;
                }}
                
                /* Responsive */
                @media screen and (max-width: 600px) {{
                    .email-content {{
                        padding: 30px 20px;
                    }}
                    
                    .btn {{
                        display: block;
                        text-align: center;
                    }}
                    
                    .order-table td {{
                        display: block;
                        text-align: left;
                        padding: 10px;
                    }}
                    
                    .order-table tr {{
                        display: block;
                        margin-bottom: 15px;
                        border-bottom: 2px solid #ddd;
                    }}
                    
                    .feature-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body style="background-color: #e3e6e6; padding: 20px;">
            <div class="email-container">
                <!-- Header -->
                <div class="email-header">
                    <div class="logo">
                        <span style="color: #ff9900;">🛒 {APP_NAME}</span>
                    </div>
                    <div class="domain-badge">
                        <span class="india-flag"></span> {DOMAIN}
                    </div>
                </div>
                
                <!-- Content -->
                <div class="email-content">
                    {content_html}
                </div>
                
                <!-- Footer -->
                <div class="email-footer">
                    <div class="footer-links">
                        <a href="http://localhost:8000">Home</a>
                        <a href="http://localhost:8000/orders">Orders</a>
                        <a href="http://localhost:8000/profile">Profile</a>
                        <a href="http://localhost:8000/help">Help</a>
                    </div>
                    <p style="margin-bottom: 10px;">
                        <span class="india-flag"></span> Made with ❤️ in India
                    </p>
                    <p style="font-size: 12px;">
                        © {current_year} {APP_NAME} | {DOMAIN}<br>
                        Need help? Contact us at <a href="mailto:{SUPPORT_EMAIL}" style="color: #ff9900;">{SUPPORT_EMAIL}</a>
                    </p>
                    <p style="font-size: 11px; color: #666; margin-top: 15px;">
                        This is a transactional email from {APP_NAME}. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """


class EmailTemplates:
    """Professional email templates matching Amazon style"""
    
    @staticmethod
    def welcome_email(user_name: str) -> Dict[str, str]:
        """Enhanced welcome email with Amazon-style design"""
        subject = f"Welcome to {APP_NAME}, {user_name}!"
        
        content_html = f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="background: #ff9900; color: #232f3e; padding: 15px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">
                <span style="font-size: 18px; font-weight: 600;">🎉 WELCOME ABOARD!</span>
            </div>
            <h1 style="color: #232f3e; font-size: 28px; margin: 15px 0;">Hello {user_name}!</h1>
            <p style="color: #666; font-size: 16px;">Thank you for joining {APP_NAME} - India's smartest shopping destination!</p>
        </div>
        
        <div class="info-box" style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 25px 0;">
            <h2 style="color: #232f3e; font-size: 18px; margin-bottom: 15px;">✨ Your account is ready!</h2>
            <p style="color: #666; margin-bottom: 20px;">You now have access to millions of products, exclusive deals, and fast delivery across India.</p>
            
            <div class="security-badge" style="display: inline-block; background: #e8f5e8; color: #28a745; padding: 8px 15px; border-radius: 20px; font-size: 13px; margin: 10px 0;">
                <i class="fas fa-shield-alt"></i> Your account is secured with 2-factor authentication
            </div>
        </div>
        
        <h3 style="color: #232f3e; font-size: 16px; margin: 25px 0 15px;">What you can do now:</h3>
        
        <div class="feature-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0;">
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">🛍️</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Shop Millions</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">1000+ products across categories</div>
            </div>
            
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">🔥</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Daily Deals</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">Up to 80% off on top brands</div>
            </div>
            
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">🚚</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Free Delivery</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">On orders above ₹500</div>
            </div>
            
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">⭐</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Wishlist</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">Save items for later</div>
            </div>
            
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">📦</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Track Orders</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">Real-time order tracking</div>
            </div>
            
            <div class="feature-item" style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e7e7e7;">
                <div class="feature-icon" style="font-size: 32px; margin-bottom: 10px;">💳</div>
                <div class="feature-title" style="color: #232f3e; font-size: 14px; font-weight: 600;">Secure Payments</div>
                <div class="feature-desc" style="color: #666; font-size: 12px;">Multiple payment options</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:8000/deals" class="btn" style="display: inline-block; padding: 14px 30px; background: #ff9900; color: #232f3e; text-decoration: none; border-radius: 8px; font-weight: 600;">🛒 Start Shopping Now</a>
            <p style="color: #666; font-size: 14px; margin-top: 15px;">Get ₹100 off on your first order! Use code: <strong style="color: #ff9900;">WELCOME100</strong></p>
        </div>
        
        <div style="text-align: center; margin-top: 25px;">
            <p style="color: #666; font-size: 14px;">Follow us for the latest updates and exclusive offers:</p>
            <div style="margin-top: 10px;">
                <a href="#" style="color: #ff9900; text-decoration: none; margin: 0 8px;">📘 Facebook</a>
                <a href="#" style="color: #ff9900; text-decoration: none; margin: 0 8px;">🐦 Twitter</a>
                <a href="#" style="color: #ff9900; text-decoration: none; margin: 0 8px;">📸 Instagram</a>
                <a href="#" style="color: #ff9900; text-decoration: none; margin: 0 8px;">📱 Telegram</a>
            </div>
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e7e7e7;">
            <p style="color: #666; font-size: 13px; text-align: center;">
                <i class="fas fa-robot"></i> Powered by SmartCartAI - Making shopping smarter every day!
            </p>
        </div>
        """
        
        full_html = EmailBaseTemplate.get_base_html(content_html, f"Welcome to {APP_NAME}, {user_name}!")
        return {"subject": subject, "html": full_html}
    
    @staticmethod
    def order_confirmation_email(user_name: str, order_data: Dict) -> Dict[str, str]:
        """Order confirmation email with Amazon-style order summary"""
        subject = f" Order Confirmed #{order_data['order_number']}"
        
        # Build items table
        items_rows = ""
        for item in order_data['items']:
            items_rows += f"""
            <tr>
                <td style="padding: 15px 12px; border-bottom: 1px solid #e7e7e7;">
                    <img src="{item['image']}" width="50" style="border-radius: 4px; vertical-align: middle; margin-right: 10px;">
                    <span style="color: #232f3e;">{item['name']}</span>
                </td>
                <td style="padding: 15px 12px; border-bottom: 1px solid #e7e7e7; text-align: center;">x{item['quantity']}</td>
                <td style="padding: 15px 12px; border-bottom: 1px solid #e7e7e7; text-align: right;" class="price">₹{item['price']}</td>
                <td style="padding: 15px 12px; border-bottom: 1px solid #e7e7e7; text-align: right;" class="price">₹{item['total']}</td>
            </tr>
            """
        
        # Calculate savings
        savings = order_data.get('savings', order_data['discount'])
        
        content_html = f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="background: #28a745; color: white; padding: 15px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">
                <span style="font-size: 18px; font-weight: 600;">✅ ORDER CONFIRMED</span>
            </div>
            <h1 style="color: #232f3e; font-size: 24px; margin: 15px 0;">Thank you, {user_name}!</h1>
            <p style="color: #666;">Your order has been confirmed and will be shipped soon.</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2 style="color: #232f3e; font-size: 16px; margin-bottom: 15px;">📦 Order Summary</h2>
            <p><strong>Order Number:</strong> #{order_data['order_number']}</p>
            <p><strong>Order Date:</strong> {order_data['order_date']}</p>
            <p><strong>Payment Method:</strong> {order_data['payment_method']}</p>
            <p><strong>Estimated Delivery:</strong> {order_data['estimated_delivery']}</p>
        </div>
        
        <h3 style="color: #232f3e; font-size: 16px; margin: 20px 0 10px;">Items Ordered:</h3>
        <table class="order-table" style="width: 100%; border-collapse: collapse; margin: 20px 0; background: #f8f9fa; border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: #232f3e; color: white;">
                    <th style="padding: 12px; text-align: left;">Item</th>
                    <th style="padding: 12px; text-align: center;">Qty</th>
                    <th style="padding: 12px; text-align: right;">Price</th>
                    <th style="padding: 12px; text-align: right;">Total</th>
                </tr>
            </thead>
            <tbody>
                {items_rows}
            </tbody>
        </table>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e7e7e7;">
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>Subtotal:</span>
                <span>₹{order_data['subtotal']}</span>
            </div>
            {f'<div style="display: flex; justify-content: space-between; padding: 8px 0; color: #28a745;"><span>Discount:</span><span>-₹{savings}</span></div>' if savings > 0 else ''}
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>Delivery:</span>
                <span style="color: #28a745;">Free</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 15px 0 0; border-top: 2px solid #e7e7e7; font-size: 18px; font-weight: 600; color: #b12704;">
                <span>Total Paid:</span>
                <span>₹{order_data['total']}</span>
            </div>
        </div>
        
        <div class="address-box" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9900;">
            <h3 style="color: #232f3e; font-size: 16px; margin-bottom: 10px;">🚚 Delivery Address</h3>
            <p style="margin: 5px 0;"><strong>{order_data['address']['recipient_name']}</strong></p>
            <p style="margin: 5px 0;">{order_data['address']['address_line1']}</p>
            {f'<p style="margin: 5px 0;">{order_data["address"]["address_line2"]}</p>' if order_data['address'].get('address_line2') else ''}
            <p style="margin: 5px 0;">{order_data['address']['city']}, {order_data['address']['state']} - {order_data['address']['zip_code']}</p>
            <p style="margin: 5px 0;">📞 {order_data['address']['phone']}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:8000/orders/{order_data['order_number']}" class="btn" style="display: inline-block; padding: 14px 30px; background: #ff9900; color: #232f3e; text-decoration: none; border-radius: 8px; font-weight: 600;">🔍 Track Your Order</a>
            <a href="http://localhost:8000" class="btn btn-secondary" style="display: inline-block; padding: 14px 30px; background: #f0f2f2; color: #232f3e; text-decoration: none; border-radius: 8px; font-weight: 600; margin-left: 10px;">🛒 Shop More</a>
        </div>
        """
        
        full_html = EmailBaseTemplate.get_base_html(content_html, f"Order Confirmed #{order_data['order_number']}")
        return {"subject": subject, "html": full_html}
    
    
    @staticmethod
    def password_reset_confirmation_email(user_name: str) -> Dict[str, str]:
        """Email sent after password is successfully reset"""
        subject = f"{APP_NAME} - Your Password Has Been Reset"
        
        content_html = f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="background: #28a745; color: white; padding: 15px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">
                <span style="font-size: 18px; font-weight: 600;">✅ PASSWORD UPDATED</span>
            </div>
            <h1 style="color: #232f3e; font-size: 24px; margin: 15px 0;">Password Changed Successfully</h1>
        </div>
        
        <div class="info-box" style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 20px 0;">
            <h2 style="color: #232f3e; font-size: 18px; margin-bottom: 15px;">Hello {user_name},</h2>
            <p style="color: #666; margin-bottom: 20px;">Your {APP_NAME} account password has been successfully changed.</p>
            
            <div class="security-badge" style="display: inline-block; background: #e8f5e8; color: #28a745; padding: 10px 20px; border-radius: 8px; font-size: 13px;">
                <i class="fas fa-check-circle"></i> This change was made on {datetime.now().strftime('%d %B %Y at %I:%M %p')}
            </div>
        </div>
        
        <div class="warning-box" style="background: #fff3cd; color: #856404; padding: 20px; border-radius: 8px; margin: 25px 0;">
            <h3 style="color: #856404; font-size: 16px; margin-bottom: 10px;">⚠️ Didn't make this change?</h3>
            <p style="color: #856404; font-size: 14px;">
                If you didn't change your password, please contact our support team immediately at <a href="mailto:{SUPPORT_EMAIL}" style="color: #ff9900;">{SUPPORT_EMAIL}</a>
            </p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:8000/login" class="btn" style="display: inline-block; padding: 14px 30px; background: #ff9900; color: #232f3e; text-decoration: none; border-radius: 8px; font-weight: 600;">🔐 Login to Your Account</a>
        </div>
        """
        
        full_html = EmailBaseTemplate.get_base_html(content_html, f"Your {APP_NAME} password has been reset")
        return {"subject": subject, "html": full_html}


class EmailService:
    """Email sending service - all config from .env"""
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP with credentials from .env"""
        try:
            print(f"\n {'='*60}")
            print(f" ATTEMPTING TO SEND EMAIL")
            print(f" TO: {to_email}")
            print(f" SUBJECT: {subject}")
            print(f" FROM: {DISPLAY_NAME} <{DISPLAY_EMAIL}>")
            print(f" SMTP: {SMTP_HOST}:{SMTP_PORT}")
            print(f"{'='*60}\n")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{DISPLAY_NAME} <{DISPLAY_EMAIL}>"
            msg['To'] = to_email
            
            # Add priority headers for faster delivery
            msg['X-Priority'] = '1'
            msg['X-MSMail-Priority'] = 'High'
            msg['Importance'] = 'High'
            
            # Attach HTML content
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            # Send email with timeout
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            logger.info(f" Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(" SMTP Authentication failed - Check your username/password in .env")
            return False
        except smtplib.SMTPException as e:
            logger.error(f" SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f" Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        print(f"\nPreparing welcome email for {user_name} ({user_email})")
        template = EmailTemplates.welcome_email(user_name)
        return EmailService.send_email(user_email, template["subject"], template["html"])
    
    @staticmethod
    def send_order_confirmation(user_email: str, user_name: str, order_data: Dict) -> bool:
        """Send order confirmation email"""
        print(f"\nPreparing order confirmation for {user_name} ({user_email})")
        print(f"Order #: {order_data['order_number']}")
        print(f" Items: {len(order_data['items'])}")
        print(f" Total: ₹{order_data['total']}")
        
        template = EmailTemplates.order_confirmation_email(user_name, order_data)
        result = EmailService.send_email(user_email, template["subject"], template["html"])
        
        if result:
            print(f" Order confirmation email sent for #{order_data['order_number']}")
        else:
            print(f" Failed to send order confirmation for #{order_data['order_number']}")
        
        return result
    
    @staticmethod
    def send_password_reset(user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        print(f"\n Preparing password reset email for {user_name} ({user_email})")
        template = EmailTemplates.password_reset_email(user_name, reset_token)
        return EmailService.send_email(user_email, template["subject"], template["html"])
    
    @staticmethod
    def send_password_reset_confirmation(user_email: str, user_name: str) -> bool:
        """Send password reset confirmation email"""
        print(f"\n Preparing password reset confirmation for {user_name} ({user_email})")
        template = EmailTemplates.password_reset_confirmation_email(user_name)
        return EmailService.send_email(user_email, template["subject"], template["html"])


class MockEmailService:
    """Mock email service for development - just logs emails"""
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        print("\n" + "="*70)
        print(f" MOCK EMAIL TO: {to_email}")
        print(f" SUBJECT: {subject}")
        print(f" FROM: {DISPLAY_NAME} <{DISPLAY_EMAIL}>")
        print("="*70)
        print(" HTML CONTENT PREVIEW:")
        print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
        print("="*70 + "\n")
        
        logger.info("="*70)
        logger.info(f" MOCK EMAIL TO: {to_email}")
        logger.info(f" SUBJECT: {subject}")
        logger.info(f" FROM: {DISPLAY_NAME} <{DISPLAY_EMAIL}>")
        logger.info("="*70)
        return True
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str) -> bool:
        print(f"\n Preparing mock welcome email for {user_name} ({user_email})")
        template = EmailTemplates.welcome_email(user_name)
        return MockEmailService.send_email(user_email, template["subject"], template["html"])
    
    @staticmethod
    def send_order_confirmation(user_email: str, user_name: str, order_data: Dict) -> bool:
        print(f"\n Preparing mock order confirmation for {user_name} ({user_email})")
        print(f" Order #: {order_data['order_number']}")
        print(f" Items: {len(order_data['items'])}")
        
        template = EmailTemplates.order_confirmation_email(user_name, order_data)
        return MockEmailService.send_email(user_email, template["subject"], template["html"])
    
    @staticmethod
    def send_password_reset(user_email: str, user_name: str, reset_token: str) -> bool:
        print(f"\n Preparing mock password reset email for {user_name} ({user_email})")
        template = EmailTemplates.password_reset_email(user_name, reset_token)
        return MockEmailService.send_email(user_email, template["subject"], template["html"])
    
    @staticmethod
    def send_password_reset_confirmation(user_email: str, user_name: str) -> bool:
        print(f"\n Preparing mock password reset confirmation for {user_name} ({user_email})")
        template = EmailTemplates.password_reset_confirmation_email(user_name)
        return MockEmailService.send_email(user_email, template["subject"], template["html"])


# Choose which service to use based on DEBUG setting
if DEBUG:
    email_service = MockEmailService()
else:
    email_service = EmailService()
