from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import random
import uuid
from typing import Optional, List

from database import get_db
from models import Order, OrderItem, User
from schemas import OrderCreate, OrderResponse, OrderDetailResponse
from utils.order_utils import log_order, generate_order_id, generate_transaction_id
from utils.email_utils import email_service  # IMPORT THE EMAIL SERVICE
from auth import get_current_user_from_cookie

router = APIRouter()

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Create a new order"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        order_id = generate_order_id()
        transaction_id = generate_transaction_id()
        delivery_days = random.randint(3, 5)
        estimated_delivery = (datetime.now() + timedelta(days=delivery_days)).strftime("%d %B, %Y")

        # Calculate final total with coupon
        discount_amount = 0
        final_total = order_data.total_amount
        
        if order_data.coupon_code:
            if order_data.coupon_code.upper() == "SAVE10":
                discount_amount = order_data.total_amount * 0.10
                final_total = order_data.total_amount * 0.9
            elif order_data.coupon_code.upper() == "WELCOME20":
                discount_amount = order_data.total_amount * 0.20
                final_total = order_data.total_amount * 0.8

        # Create order in database
        order = Order(
            id=str(uuid.uuid4()),
            order_number=order_id,
            user_id=current_user.id,
            transaction_id=transaction_id,
            total_amount=order_data.total_amount,
            discount_amount=discount_amount,
            final_amount=final_total,
            payment_method=order_data.payment_method,
            shipping_address=order_data.shipping_address.dict(),
            coupon_code=order_data.coupon_code,
            estimated_delivery=estimated_delivery,
            order_date=datetime.now(),
            order_status="confirmed",
            payment_status="completed"
        )
        db.add(order)
        db.flush()

        # Add order items
        for item in order_data.items:
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_image=item.product_image,
                quantity=item.quantity,
                price=item.price,
                total=item.price * item.quantity
            )
            db.add(order_item)

        db.commit()

        # Prepare COMPLETE order data for email
        order_email_data = {
            "order_number": order_id,
            "order_date": datetime.now().strftime("%d %B, %Y"),
            "items": [
                {
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "price": float(item.price),
                    "total": float(item.price * item.quantity),
                    "image": item.product_image or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100"
                }
                for item in order_data.items
            ],
            "subtotal": float(order_data.total_amount),
            "discount": float(discount_amount),
            "savings": float(discount_amount),
            "total": float(final_total),
            "payment_method": order_data.payment_method.replace('_', ' ').title(),
            "estimated_delivery": estimated_delivery,
            "address": {
                "recipient_name": order_data.shipping_address.recipient_name,
                "phone": order_data.shipping_address.phone,
                "address_line1": order_data.shipping_address.address_line1,
                "address_line2": order_data.shipping_address.address_line2 or "",
                "city": order_data.shipping_address.city,
                "state": order_data.shipping_address.state,
                "zip_code": order_data.shipping_address.zip_code
            }
        }

        # Send order confirmation email using the email_service
        background_tasks.add_task(
            email_service.send_order_confirmation,
            current_user.email,
            current_user.first_name,
            order_email_data
        )

        # Background tasks for logging
        background_tasks.add_task(log_order, {
            "order_id": order_id,
            "total": final_total,
            "customer": {
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email
            },
            "products": [item.dict() for item in order_data.items]
        })

        return OrderResponse(
            success=True,
            order_id=order_id,
            transaction_id=transaction_id,
            message=f"Order placed successfully! Your order will be delivered by {estimated_delivery}",
            amount=final_total,
            estimated_delivery=estimated_delivery
        )

    except Exception as e:
        db.rollback()
        print(f"❌ Order creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/orders")
async def get_user_orders(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Get user's orders with filtering and pagination"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    # Filter by status
    if status and status != "all":
        query = query.filter(Order.order_status == status)
    
    # Search by order number or product name
    if search:
        query = query.filter(
            or_(
                Order.order_number.ilike(f"%{search}%"),
                Order.items.any(OrderItem.product_name.ilike(f"%{search}%"))
            )
        )
    
    # Get total count
    total = query.count()
    
    # Pagination
    orders = query.order_by(Order.order_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Format response
    result = []
    for order in orders:
        items = []
        for item in order.items:
            items.append({
                "product_id": item.product_id,
                "name": item.product_name,
                "image": item.product_image,
                "quantity": item.quantity,
                "price": float(item.price),
                "total": float(item.total)
            })
        
        # Determine display date
        display_date = ""
        if order.order_status == "delivered" and order.delivered_date:
            display_date = order.delivered_date.strftime("%d %B, %Y")
        else:
            display_date = order.estimated_delivery or order.order_date.strftime("%d %B, %Y")
        
        result.append({
            "order_number": order.order_number,
            "order_date": order.order_date.strftime("%d %B, %Y") if order.order_date else None,
            "total_amount": float(order.total_amount),
            "discount_amount": float(order.discount_amount),
            "final_amount": float(order.final_amount),
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "payment_method": order.payment_method,
            "estimated_delivery": order.estimated_delivery,
            "delivered_date": order.delivered_date.strftime("%d %B, %Y") if order.delivered_date else None,
            "display_date": display_date,
            "date_label": "Delivered on" if order.order_status == "delivered" else "Estimated delivery",
            "items": items,
            "can_cancel": order.order_status in ["confirmed", "processing"],
            "can_return": order.order_status == "delivered" and order.delivered_date and 
                         (datetime.now() - order.delivered_date).days <= 30,
            "can_reorder": True,
            "tracking_steps": get_tracking_steps(order.order_status, order.delivered_date)
        })
    
    return {
        "orders": result,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/orders/{order_number}", response_model=OrderDetailResponse)
async def get_order_details(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Get detailed order information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items
    items = []
    for item in order.items:
        items.append({
            "product_id": item.product_id,
            "name": item.product_name,
            "image": item.product_image,
            "quantity": item.quantity,
            "price": float(item.price),
            "total": float(item.total)
        })
    
    # Get tracking timeline
    tracking_steps = get_tracking_steps(order.order_status, order.delivered_date)
    
    return OrderDetailResponse(
        order_number=order.order_number,
        transaction_id=order.transaction_id,
        order_date=order.order_date.strftime("%d %B, %Y %I:%M %p") if order.order_date else None,
        total_amount=float(order.total_amount),
        discount_amount=float(order.discount_amount),
        final_amount=float(order.final_amount),
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        order_status=order.order_status,
        shipping_address=order.shipping_address,
        estimated_delivery=order.estimated_delivery,
        delivered_date=order.delivered_date.strftime("%d %B, %Y") if order.delivered_date else None,
        items=items,
        tracking_steps=tracking_steps
    )

def get_tracking_steps(status: str, delivered_date=None):
    """Generate tracking timeline steps"""
    today = datetime.now().strftime("%d %b")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d %b")
    
    steps = [
        {"name": "Order Placed", "status": "completed", "date": today, "icon": "fa-check-circle"},
        {"name": "Processing", "status": "completed" if status not in ["confirmed"] else "in_progress", 
         "date": today if status not in ["confirmed"] else "Processing", "icon": "fa-cog"},
        {"name": "Shipped", "status": "completed" if status in ["shipped", "delivered"] else "pending", 
         "date": tomorrow if status in ["shipped", "delivered"] else "Pending", "icon": "fa-truck"},
        {"name": "Delivered", "status": "completed" if status == "delivered" else "pending", 
         "date": delivered_date.strftime("%d %b") if delivered_date else "Estimated: 3-5 days", 
         "icon": "fa-home"}
    ]
    return steps

@router.post("/orders/{order_number}/cancel")
async def cancel_order(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Cancel an order"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status not in ["confirmed", "processing"]:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")
    
    order.order_status = "cancelled"
    order.payment_status = "refunded"
    db.commit()
    
    return {"success": True, "message": "Order cancelled successfully"}

@router.post("/orders/{order_number}/return")
async def return_order(
    order_number: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Return an order"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_status != "delivered":
        raise HTTPException(status_code=400, detail="Only delivered orders can be returned")
    
    if order.delivered_date and (datetime.now() - order.delivered_date).days > 30:
        raise HTTPException(status_code=400, detail="Return period has expired (30 days)")
    
    order.order_status = "returned"
    order.payment_status = "refunded"
    order.cancellation_reason = reason
    db.commit()
    
    return {"success": True, "message": "Return request submitted successfully"}

@router.post("/orders/{order_number}/reorder")
async def reorder(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Reorder items from a previous order"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    order = db.query(Order).filter(
        Order.order_number == order_number,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Create cart items from order
    from crud import CartCRUD
    cart = CartCRUD.get_by_user(db, current_user.id)
    
    for item in order.items:
        CartCRUD.add_item(db, current_user.id, item.product_id, item.quantity)
    
    return {"success": True, "message": "Items added to cart"}