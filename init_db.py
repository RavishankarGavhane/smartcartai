#!/usr/bin/env python3
"""
Database initialization script for SmartCartAI
Loads products from data.py into PostgreSQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime, UTC
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, engine
from models import Product
from data import products
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and products from data.py"""
    logger.info("Initializing SmartCartAI Database...")
    
    # Create tables
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully!")
    
    # Create session
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Check if products already exist
        existing_count = db.query(Product).count()
        
        if existing_count == 0:
            logger.info(f"Loading {len(products)} products from data.py...")
            
            for prod_data in products:
                product = Product(
                    id=prod_data["id"],
                    name=prod_data["name"],
                    price=float(prod_data["price"]),
                    original_price=float(prod_data["original_price"]) if prod_data.get("original_price") else None,
                    discount=prod_data.get("discount", 0),
                    category=prod_data["category"],
                    subcategory=prod_data.get("subcategory"),
                    rating=float(prod_data.get("rating", 0)),
                    reviews=prod_data.get("reviews", 0),
                    image=prod_data["image"],
                    badge=prod_data.get("badge"),
                    delivery=prod_data.get("delivery"),
                    prime=prod_data.get("prime", False),
                    assured=prod_data.get("assured", False),
                    bank_offers=prod_data.get("bank_offers"),
                    colors=prod_data.get("colors"),
                    sizes=prod_data.get("sizes"),
                    config=prod_data.get("config"),
                    in_stock=prod_data.get("in_stock", True),
                    created_at=datetime.now(UTC)
                )
                db.add(product)
            
            db.commit()
            logger.info(f"Successfully loaded {len(products)} products into database!")
        else:
            logger.info(f"Database already has {existing_count} products. Skipping import.")
        
        # Create indexes
        logger.info(" Creating indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);"))
        db.commit()
        logger.info("Indexes created successfully!")
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f" Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()