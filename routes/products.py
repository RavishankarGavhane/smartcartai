from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from sqlalchemy.orm import Session

from database import get_db
from crud import ProductCRUD
from schemas import ProductBase, ProductDetail, ProductListResponse

router = APIRouter()

@router.get("/products", response_model=ProductListResponse)
async def get_products(
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    products = ProductCRUD.get_all(
        db=db,
        category=category,
        subcategory=subcategory,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        limit=limit,
        offset=offset
    )
    
    # Convert SQLAlchemy objects to dict for Pydantic
    product_list = []
    for p in products:
        product_list.append(
            ProductBase(
                id=p.id,
                name=p.name,
                price=float(p.price),
                original_price=float(p.original_price) if p.original_price else None,
                discount=p.discount,
                category=p.category,
                subcategory=p.subcategory,
                rating=float(p.rating) if p.rating else 0,
                reviews=p.reviews,
                image=p.image,
                badge=p.badge,
                delivery=p.delivery,
                prime=p.prime,
                assured=p.assured,
                bank_offers=p.bank_offers,
                colors=p.colors,
                sizes=p.sizes,
                config=p.config,
                in_stock=p.in_stock
            )
        )
    
    return ProductListResponse(
        products=product_list,
        total=len(product_list),
        page=page,
        limit=limit
    )

@router.get("/products/{product_id}", response_model=ProductDetail)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    p = ProductCRUD.get_by_id(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductDetail(
        id=p.id,
        name=p.name,
        price=float(p.price),
        original_price=float(p.original_price) if p.original_price else None,
        discount=p.discount,
        category=p.category,
        subcategory=p.subcategory,
        rating=float(p.rating) if p.rating else 0,
        reviews=p.reviews,
        image=p.image,
        badge=p.badge,
        delivery=p.delivery,
        prime=p.prime,
        assured=p.assured,
        bank_offers=p.bank_offers,
        colors=p.colors,
        sizes=p.sizes,
        config=p.config,
        in_stock=p.in_stock
    )

@router.get("/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    return ProductCRUD.get_categories(db)

@router.get("/subcategories/{category}", response_model=List[str])
async def get_subcategories(
    category: str,
    db: Session = Depends(get_db)
):
    return ProductCRUD.get_subcategories(db, category)

@router.get("/deals", response_model=List[ProductBase])
async def get_deals(db: Session = Depends(get_db)):
    deals = ProductCRUD.get_deals(db)
    product_list = []
    for p in deals:
        product_list.append(
            ProductBase(
                id=p.id,
                name=p.name,
                price=float(p.price),
                original_price=float(p.original_price) if p.original_price else None,
                discount=p.discount,
                category=p.category,
                subcategory=p.subcategory,
                rating=float(p.rating) if p.rating else 0,
                reviews=p.reviews,
                image=p.image,
                badge=p.badge,
                delivery=p.delivery,
                prime=p.prime,
                assured=p.assured,
                bank_offers=p.bank_offers,
                colors=p.colors,
                sizes=p.sizes,
                config=p.config,
                in_stock=p.in_stock
            )
        )
    return product_list
