"""Product router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from schemas.product import Product, ProductCreate, ProductUpdate
from crud.product import product_crud

router = APIRouter()


@router.get("/", response_model=List[Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve products."""
    products = product_crud.get_multi(db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product."""
    return product_crud.create(db=db, obj_in=product)


@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    db_product = product_crud.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product."""
    db_product = product_crud.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_crud.update(db=db, db_obj=db_product, obj_in=product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete a product."""
    db_product = product_crud.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_crud.remove(db=db, id=product_id)
    return {"message": "Product deleted successfully"}
