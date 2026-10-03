import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from app.db.database import get_db, Product
from app.cache.redis_client import cache

router = APIRouter(prefix="/products", tags=["Products"])
CACHE_KEY = "products:all"


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    stock: int
    source: str = ""


@router.get("", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return [ProductResponse(**item, source="Redis ⚡") for item in cached]

    products = db.query(Product).all()
    result = [{"id": p.id, "name": p.name, "category": p.category, "price": p.price, "stock": p.stock} for p in products]
    cache.set(CACHE_KEY, result, ttl=60)
    return [ProductResponse(**item, source="PostgreSQL 🗄️") for item in result]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(prod: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(id=f"PROD-{uuid.uuid4().hex[:8].upper()}", name=prod.name, category=prod.category, price=prod.price, stock=prod.stock)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    cache.delete(CACHE_KEY)
    return ProductResponse(id=new_product.id, name=new_product.name, category=new_product.category, price=new_product.price, stock=new_product.stock, source="PostgreSQL ✅")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(product)
    db.commit()
    cache.delete(CACHE_KEY)
    return None