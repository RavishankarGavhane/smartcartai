from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# User Schemas
class UserBase(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=50)
    lastName: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=10)
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be 10 digits')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be 10 digits')
        return v

class UserResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    phone: str
    createdAt: Optional[str] = None
    isVerified: bool = False
    addresses: List[Dict] = []
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None

# Address Schemas - Fully Dynamic, No Hardcoded Examples
class AddressBase(BaseModel):
    type: str = "home"
    recipient_name: str
    phone: str = Field(..., min_length=10, max_length=10)
    address_line1: str
    address_line2: Optional[str] = ""
    landmark: Optional[str] = None
    city: str
    state: str
    zip_code: str = Field(..., min_length=6, max_length=6)
    is_default: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be 10 digits')
        return v
    
    @validator('zip_code')
    def validate_zip(cls, v):
        if not re.match(r'^[0-9]{6}$', v):
            raise ValueError('PIN code must be 6 digits')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['home', 'work', 'other']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of {allowed_types}')
        return v

class AddressCreate(AddressBase):
    """Schema for creating a new address"""
    pass

class AddressUpdate(BaseModel):
    """Schema for updating an existing address - all fields optional"""
    type: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=10)
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = Field(None, min_length=6, max_length=6)
    is_default: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be 10 digits')
        return v
    
    @validator('zip_code')
    def validate_zip(cls, v):
        if v and not re.match(r'^[0-9]{6}$', v):
            raise ValueError('PIN code must be 6 digits')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if v:
            allowed_types = ['home', 'work', 'other']
            if v not in allowed_types:
                raise ValueError(f'Type must be one of {allowed_types}')
        return v

class AddressResponse(AddressBase):
    """Schema for address response"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    full_address: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @validator('full_address', always=True)
    def generate_full_address(cls, v, values):
        """Generate full address string from components"""
        parts = []
        if values.get('address_line1'):
            parts.append(values['address_line1'])
        if values.get('address_line2'):
            parts.append(values['address_line2'])
        if values.get('landmark'):
            parts.append(f"Near {values['landmark']}")
        if values.get('city'):
            parts.append(values['city'])
        if values.get('state'):
            parts.append(values['state'])
        if values.get('zip_code'):
            parts.append(values['zip_code'])
        return ', '.join(parts) if parts else None

class AddressListResponse(BaseModel):
    """Schema for list of addresses response"""
    addresses: List[AddressResponse]
    total: int
    default_address_id: Optional[str] = None

class AddressDeleteResponse(BaseModel):
    """Schema for address deletion response"""
    success: bool
    message: str
    deleted_address_id: str

# Product Schemas
class ProductBase(BaseModel):
    id: int
    name: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[int] = 0
    category: str
    subcategory: Optional[str] = None
    rating: float = 0
    reviews: int = 0
    image: str
    badge: Optional[str] = None
    delivery: Optional[str] = None
    prime: bool = False
    assured: bool = False
    bank_offers: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    config: Optional[List[str]] = None
    in_stock: bool = True

class ProductDetail(ProductBase):
    description: Optional[str] = None
    specifications: Optional[Dict] = None

class ProductListResponse(BaseModel):
    products: List[ProductBase]
    total: int
    page: int
    limit: int

# Cart Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1)

class CartItemResponse(BaseModel):
    id: str
    product_id: int
    name: str
    price: float
    quantity: int
    subtotal: float
    image: str

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float
    total_items: int

# Order Schemas
class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    quantity: int = Field(1, ge=1)
    price: float

class ShippingAddress(BaseModel):
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = ""
    city: str
    state: str
    zip_code: str
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be 10 digits')
        return v

class OrderCreate(BaseModel):
    items: List[OrderItemBase]
    shipping_address: ShippingAddress
    payment_method: str
    coupon_code: Optional[str] = None
    total_amount: float

class OrderResponse(BaseModel):
    success: bool
    order_id: str
    transaction_id: str
    message: str
    amount: float
    estimated_delivery: str

class OrderDetailResponse(BaseModel):
    order_number: str
    transaction_id: Optional[str] = None
    order_date: Optional[str] = None
    total_amount: float
    discount_amount: float = 0
    final_amount: float
    payment_method: str
    payment_status: str
    order_status: str
    shipping_address: Dict
    estimated_delivery: Optional[str] = None
    items: List[Dict]
    tracking_steps: Optional[List[Dict]] = None

# Session Schema
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    detail: str

# Coupon Schema
class CouponApply(BaseModel):
    code: str
    cart_total: float

class CouponResponse(BaseModel):
    success: bool
    message: str
    discount_amount: float
    final_total: float

# Search Schema
class SearchResponse(BaseModel):
    query: str
    results: List[ProductBase]
    total: int

# Category Schema
class CategoryResponse(BaseModel):
    name: str
    count: Optional[int] = None

class SubcategoryResponse(BaseModel):
    name: str
    category: str
    count: Optional[int] = None

# Payment Schema
class PaymentMethod(BaseModel):
    id: str
    name: str
    icon: str
    enabled: bool = True

# Wishlist Schema
class WishlistItemResponse(BaseModel):
    id: str
    product_id: int
    product_name: str
    product_price: float
    product_image: str
    added_at: str

# Review Schema
class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    user_name: str
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    created_at: str
    is_verified_purchase: bool = False

# Stats Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    database: str
    products_count: Optional[int] = None
    orders_count: Optional[int] = None

class StatsResponse(BaseModel):
    total_products: int
    categories: List[str]
    total_orders: Optional[int] = None
    total_revenue: Optional[float] = None