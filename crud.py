from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any
import random
from models import User, Product, Order, OrderItem, Cart, CartItem, Address, Session as DBSession
from auth_utils import get_password_hash
from utils.order_utils import generate_order_id, generate_transaction_id, calculate_delivery_date

# User CRUD
class UserCRUD:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    def create(db: Session, first_name: str, last_name: str, email: str, phone: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        user_id = str(uuid.uuid4())
        
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=hashed_password
        )
        db.add(user)
        db.flush()
        
        # Create cart for user
        cart = Cart(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(cart)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

# Session CRUD
class SessionCRUD:
    @staticmethod
    def create(db: Session, user_id: str, token: str, user_agent: str = None, ip: str = None) -> DBSession:
        session = DBSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=token,
            user_agent=user_agent,
            ip_address=ip,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(session)
        db.commit()
        return session
    
    @staticmethod
    def get_by_token(db: Session, token: str) -> Optional[DBSession]:
        return db.query(DBSession).filter(
            DBSession.token == token,
            DBSession.is_active == True,
            DBSession.expires_at > datetime.utcnow()
        ).first()
    
    @staticmethod
    def deactivate(db: Session, token: str):
        session = db.query(DBSession).filter(DBSession.token == token).first()
        if session:
            session.is_active = False
            db.commit()

# Product CRUD
class ProductCRUD:
    @staticmethod
    def get_all(
        db: Session,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Product]:
        query = db.query(Product)
        
        if category and category != "all":
            query = query.filter(Product.category == category)
        
        if subcategory and subcategory != "all":
            query = query.filter(Product.subcategory == subcategory)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Product.name.ilike(search_term))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if sort == "price_low":
            query = query.order_by(Product.price.asc())
        elif sort == "price_high":
            query = query.order_by(Product.price.desc())
        elif sort == "rating":
            query = query.order_by(Product.rating.desc())
        elif sort == "discount":
            query = query.order_by(Product.discount.desc())
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_deals(db: Session, limit: int = 10) -> List[Product]:
        return db.query(Product).filter(
            Product.discount >= 20
        ).order_by(
            Product.discount.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_categories(db: Session) -> List[str]:
        return [c[0] for c in db.query(Product.category).distinct().order_by(Product.category).all()]
    
    @staticmethod
    def get_subcategories(db: Session, category: str) -> List[str]:
        return [s[0] for s in db.query(Product.subcategory).filter(
            Product.category == category,
            Product.subcategory.isnot(None)
        ).distinct().order_by(Product.subcategory).all()]

# Cart CRUD
class CartCRUD:
    @staticmethod
    def get_by_user(db: Session, user_id: str) -> Optional[Cart]:
        return db.query(Cart).filter(Cart.user_id == user_id).first()
    
    @staticmethod
    def add_item(db: Session, user_id: str, product_id: int, quantity: int = 1) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(id=str(uuid.uuid4()), user_id=user_id)
            db.add(cart)
            db.flush()
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                id=str(uuid.uuid4()),
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price_at_time=float(product.price)
            )
            db.add(cart_item)
        
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def update_quantity(db: Session, user_id: str, product_id: int, quantity: int) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ValueError("Cart not found")
        
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        
        if not cart_item:
            raise ValueError("Item not in cart")
        
        if quantity <= 0:
            db.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def remove_item(db: Session, user_id: str, product_id: int) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if cart:
            db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            ).delete()
            db.commit()
            db.refresh(cart)
        return cart
    
    @staticmethod
    def clear(db: Session, user_id: str):
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if cart:
            db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            db.commit()
    
    @staticmethod
    def get_cart_details(db: Session, user_id: str) -> Dict:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            return {"items": [], "total": 0, "total_items": 0}
        
        items = []
        for item in cart.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "name": product.name if product else "Unknown",
                "price": float(item.price_at_time),
                "quantity": item.quantity,
                "subtotal": float(item.subtotal),
                "image": product.image if product else ""
            })
        
        return {
            "items": items,
            "total": float(cart.total),
            "total_items": cart.total_items
        }

# Order CRUD
class OrderCRUD:
    @staticmethod
    def create(db: Session, user_id: str, order_data: Dict) -> Order:
        order_number = generate_order_id()
        transaction_id = generate_transaction_id()
        estimated_delivery = calculate_delivery_date(random.randint(3, 5))
        
        order = Order(
            id=str(uuid.uuid4()),
            order_number=order_number,
            user_id=user_id,
            transaction_id=transaction_id,
            total_amount=order_data["total_amount"],
            discount_amount=order_data.get("discount_amount", 0),
            final_amount=order_data["final_amount"],
            payment_method=order_data["payment_method"],
            shipping_address=order_data["shipping_address"],
            coupon_code=order_data.get("coupon_code"),
            estimated_delivery=estimated_delivery
        )
        db.add(order)
        db.flush()
        
        for item in order_data["items"]:
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order.id,
                product_id=item["product_id"],
                product_name=item["product_name"],
                product_image=item.get("product_image", ""),
                quantity=item["quantity"],
                price=item["price"],
                total=item["price"] * item["quantity"]
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_user_orders(db: Session, user_id: str) -> List[Order]:
        return db.query(Order).filter(
            Order.user_id == user_id
        ).order_by(
            Order.order_date.desc()
        ).all()
    
    @staticmethod
    def get_by_order_number(db: Session, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number).first()

# Address CRUD
class AddressCRUD:
    @staticmethod
    def create(db: Session, user_id: str, address_data: Dict) -> Address:
        if address_data.get("is_default"):
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.is_default == True
            ).update({"is_default": False})
        
        address = Address(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=address_data.get("type", "home"),
            recipient_name=address_data["recipient_name"],
            phone=address_data["phone"],
            address_line1=address_data["address_line1"],
            address_line2=address_data.get("address_line2", ""),
            city=address_data["city"],
            state=address_data["state"],
            zip_code=address_data["zip_code"],
            is_default=address_data.get("is_default", False)
        )
        db.add(address)
        db.commit()
        db.refresh(address)
        return address
    
    @staticmethod
    def get_user_addresses(db: Session, user_id: str) -> List[Address]:
        return db.query(Address).filter(
            Address.user_id == user_id
        ).order_by(
            Address.is_default.desc(),
            Address.created_at.desc()
        ).all()