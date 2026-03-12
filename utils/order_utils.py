import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logger
logger = logging.getLogger(__name__)

def generate_order_id() -> str:
    """
    Generate a unique order ID in format: ORD-YYYYMMDD-XXXXXX
    Example: ORD-20240315-123456
    """
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"ORD-{date_part}-{random_part}"

def generate_transaction_id() -> str:
    """
    Generate a unique transaction ID in format: TXN-YYYYMMDDHHMMSS-XXXX
    Example: TXN-20240315143022-1234
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = random.randint(1000, 9999)
    return f"TXN-{timestamp}-{random_part}"

def calculate_delivery_date(days: int = 3) -> str:
    """
    Calculate estimated delivery date
    Returns date in format: "15 March, 2024"
    """
    delivery_date = datetime.now() + timedelta(days=days)
    return delivery_date.strftime("%d %B, %Y")

def format_order_date(date: datetime) -> str:
    """
    Format order date for display
    Returns date in format: "15 March, 2024"
    """
    if not date:
        return "N/A"
    return date.strftime("%d %B, %Y")

def format_datetime(date: datetime) -> str:
    """
    Format datetime for display with time
    Returns in format: "15 March, 2024 02:30 PM"
    """
    if not date:
        return "N/A"
    return date.strftime("%d %B, %Y %I:%M %p")

def get_tracking_steps(status: str, delivered_date: Optional[datetime] = None) -> List[Dict]:
    """
    Generate tracking timeline steps based on order status
    Returns list of steps with status and dates
    """
    steps = [
        {
            "name": "Order Placed",
            "status": "completed",
            "date": "Today",
            "icon": "fa-check-circle"
        },
        {
            "name": "Processing",
            "status": "in_progress",
            "date": "Today",
            "icon": "fa-spinner"
        },
        {
            "name": "Shipped",
            "status": "pending",
            "date": "Tomorrow",
            "icon": "fa-truck"
        },
        {
            "name": "Delivered",
            "status": "pending",
            "date": "Estimated: 3-5 days",
            "icon": "fa-home"
        }
    ]
    
    # Update status based on actual order status
    if status in ["confirmed", "processing", "shipped", "delivered"]:
        steps[0]["status"] = "completed"
        steps[0]["date"] = datetime.now().strftime("%d %b")
    
    if status in ["processing", "shipped", "delivered"]:
        steps[1]["status"] = "completed"
        steps[1]["date"] = datetime.now().strftime("%d %b")
    elif status == "confirmed":
        steps[1]["status"] = "in_progress"
    
    if status in ["shipped", "delivered"]:
        steps[2]["status"] = "completed"
        steps[2]["date"] = (datetime.now() - timedelta(days=1)).strftime("%d %b")
    elif status == "processing":
        steps[2]["status"] = "in_progress"
    
    if status == "delivered":
        steps[3]["status"] = "completed"
        if delivered_date:
            steps[3]["date"] = delivered_date.strftime("%d %b")
        else:
            steps[3]["date"] = datetime.now().strftime("%d %b")
    elif status == "shipped":
        steps[3]["status"] = "in_progress"
        steps[3]["date"] = "Expected tomorrow"
    elif status == "cancelled":
        # If cancelled, mark all as cancelled
        for step in steps:
            step["status"] = "cancelled"
            step["icon"] = "fa-times-circle"
        steps[0]["date"] = datetime.now().strftime("%d %b")
    
    return steps

def log_order(order_data: Dict):
    """
    Log order details for tracking
    """
    try:
        logger.info(f"Order processed: {order_data.get('order_id')} for ₹{order_data.get('total', 0)}")
        customer = order_data.get('customer', {})
        logger.info(f"Customer: {customer.get('firstName')} {customer.get('lastName')} ({customer.get('email')})")
        logger.info(f"Items: {len(order_data.get('products', []))} products")
        
        # Log each item
        for idx, product in enumerate(order_data.get('products', []), 1):
            logger.info(f"  {idx}. {product.get('name')} x{product.get('quantity')} - ₹{product.get('price')}")
            
    except Exception as e:
        logger.error(f"Error logging order: {str(e)}")

def send_order_confirmation(email: str, order_id: str):
    """
    Simulate sending order confirmation email
    In production, this would integrate with an email service
    """
    logger.info(f"📧 Order confirmation email sent to {email} for order {order_id}")
    # Here you would add actual email sending logic
    # e.g., using SMTP, SendGrid, AWS SES, etc.

def calculate_order_summary(items: List[Dict]) -> Dict:
    """
    Calculate order summary from items
    Returns dict with subtotal, tax, shipping, total
    """
    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
    tax = subtotal * 0.18  # 18% GST (example)
    shipping = 0 if subtotal > 500 else 40  # Free shipping above ₹500
    
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "shipping": shipping,
        "total": round(subtotal + tax + shipping, 2)
    }

def validate_coupon(code: str, total: float) -> Dict:
    """
    Validate and apply coupon code
    Returns dict with success status, discount amount, and message
    """
    coupons = {
        "SAVE10": {"discount": 0.10, "min_amount": 0, "description": "10% off on entire order"},
        "WELCOME20": {"discount": 0.20, "min_amount": 1000, "description": "20% off on orders above ₹1000"},
        "FREESHIP": {"discount": 0, "free_shipping": True, "description": "Free shipping on your order"},
        "DIWALI25": {"discount": 0.25, "min_amount": 2000, "description": "25% off on orders above ₹2000"},
    }
    
    code = code.upper()
    
    if code not in coupons:
        return {
            "success": False,
            "message": "Invalid coupon code",
            "discount_amount": 0,
            "final_total": total
        }
    
    coupon = coupons[code]
    
    # Check minimum amount requirement
    if "min_amount" in coupon and total < coupon["min_amount"]:
        return {
            "success": False,
            "message": f"This coupon requires minimum order of ₹{coupon['min_amount']}",
            "discount_amount": 0,
            "final_total": total
        }
    
    # Calculate discount
    discount_amount = total * coupon.get("discount", 0) if "discount" in coupon else 0
    
    # Apply free shipping if applicable
    shipping_discount = 40 if coupon.get("free_shipping") and total < 500 else 0
    total_discount = discount_amount + shipping_discount
    
    return {
        "success": True,
        "message": f"Coupon applied: {coupon['description']}",
        "discount_amount": round(total_discount, 2),
        "final_total": round(total - total_discount, 2),
        "free_shipping": coupon.get("free_shipping", False)
    }

def get_order_status_display(status: str) -> Dict:
    """
    Get display information for order status
    Returns dict with label, color, icon
    """
    status_map = {
        "confirmed": {
            "label": "Confirmed",
            "color": "#1976d2",
            "bg_color": "#e3f2fd",
            "icon": "fa-check-circle"
        },
        "processing": {
            "label": "Processing",
            "color": "#f57c00",
            "bg_color": "#fff3e0",
            "icon": "fa-cog"
        },
        "shipped": {
            "label": "Shipped",
            "color": "#3f51b5",
            "bg_color": "#e8eaf6",
            "icon": "fa-shipping-fast"
        },
        "delivered": {
            "label": "Delivered",
            "color": "#388e3c",
            "bg_color": "#e8f5e8",
            "icon": "fa-check-circle"
        },
        "cancelled": {
            "label": "Cancelled",
            "color": "#c62828",
            "bg_color": "#ffebee",
            "icon": "fa-times-circle"
        },
        "returned": {
            "label": "Returned",
            "color": "#7b1fa2",
            "bg_color": "#f3e5f5",
            "icon": "fa-undo"
        }
    }
    
    return status_map.get(status, {
        "label": status.capitalize(),
        "color": "#666",
        "bg_color": "#f5f5f5",
        "icon": "fa-clock"
    })

def can_cancel_order(status: str) -> bool:
    """Check if order can be cancelled"""
    return status in ["confirmed", "processing"]

def can_return_order(status: str, delivered_date: Optional[datetime] = None) -> bool:
    """Check if order can be returned (within 30 days of delivery)"""
    if status != "delivered" or not delivered_date:
        return False
    
    days_since_delivery = (datetime.now() - delivered_date).days
    return days_since_delivery <= 30

def estimate_delivery_date(pincode: str, product_category: str) -> str:
    """
    Estimate delivery date based on pincode and product category
    Simple simulation - in production, integrate with logistics API
    """
    # Simulate delivery days based on pincode region
    metro_cities = ["400001", "110001", "700001", "600001"]  # Mumbai, Delhi, Kolkata, Chennai
    base_days = 2 if pincode[:2] in ["40", "11", "70", "60"] else 3
    
    # Add days based on product category
    category_days = {
        "electronics": 1,
        "fashion": 0,
        "footwear": 0,
        "home": 2,
        "books": 0,
        "sports": 1,
        "toys": 0
    }
    
    total_days = base_days + category_days.get(product_category, 1)
    
    delivery_date = datetime.now() + timedelta(days=total_days)
    return delivery_date.strftime("%d %B, %Y")

def generate_invoice_number(order_id: str) -> str:
    """Generate invoice number from order ID"""
    return f"INV-{order_id[4:]}"  # Convert ORD-20240315-123456 to INV-20240315-123456