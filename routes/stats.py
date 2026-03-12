from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func

from database import get_db
from models import Product, Order
from schemas import HealthResponse, StatsResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1").first()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    products_count = db.query(func.count(Product.id)).scalar()
    orders_count = db.query(func.count(Order.id)).scalar()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="SmartCartAI",
        version="2.0.0",
        database=db_status,
        products_count=products_count,
        orders_count=orders_count
    )

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    total_products = db.query(func.count(Product.id)).scalar()
    categories = [c[0] for c in db.query(Product.category).distinct().all()]
    total_orders = db.query(func.count(Order.id)).scalar()
    
    # Calculate total revenue
    total_revenue_result = db.query(func.sum(Order.final_amount)).scalar()
    total_revenue = float(total_revenue_result) if total_revenue_result else 0
    
    return StatsResponse(
        total_products=total_products,
        categories=categories,
        total_orders=total_orders,
        total_revenue=total_revenue
    )