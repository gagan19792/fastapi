from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from product.schema import Product
from database import engine, SessionLocal
from product import models
from fastapi.params import Depends
from product import schema

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products/")
def add_product(productRequest: Product, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=productRequest.name,
        description=productRequest.description,
        price=productRequest.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@app.get("/product/{product_id}")
def get_products(product_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.id == product_id).first()
    return products

@app.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.id == product_id).first()
    if products:
        db.delete(products)
        db.commit()
        return f"Product with id {product_id} has been deleted."
    return {"error": "Product not found"}

@app.put("/product/{product_id}")
def update_product(product_id: int, product:schemas.Product, db: Session = Depends(get_db)):
    product_query = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product_query:
        return {"error": "Product not found"}
    product_query.update(product.dump())
    db.commit()
    db.refresh(product_query)
    return product_query