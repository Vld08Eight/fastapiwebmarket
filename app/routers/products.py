from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert
from slugify import slugify
from sqlalchemy import select, update

from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from app.models.category import Category
from app.models.products import Product

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if len(products) > 0:
        return products
    else:
        return {
            'status_code': status.HTTP_404_NOT_FOUND,
            'transaction': '404 product not found'
        }


@router.post('/')
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    category = db.scalar(select(Category).where(Category.id == create_product.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    
    slug = slugify(create_product.name)
    
    existing_product = db.scalar(select(Product).where(Product.slug == slug))

    if existing_product:
        counter = 1
        while True:
            new_slug = f"{slug}-{counter}"
            # Check again with the new slug
            existing = db.scalar(select(Product).where(Product.slug == new_slug))
            if not existing:
                slug = new_slug
                break
            counter += 1
    
    db.execute(
        insert(Product).values(
            name=create_product.name,
            description=create_product.description,
            price=create_product.price,
            rating=0.0,
            image_url=create_product.image_url,
            stock=create_product.stock,


            slug=slug,
            
            category_id=create_product.category,
            is_active=True  # Explicitly setting is_active (optional if default is set in model)
        )
    )
    db.commit()
    
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    subcategories = db.scalars(select(Category).where(Category.parent_id == category.id)).all()
    categories_and_subcategories = [category.id] + [i.id for i in subcategories]
    products_category = db.scalars(
        select(Product).where(Product.category_id.in_(categories_and_subcategories), Product.is_active == True,
                              Product.stock > 0)).all()
    return products_category


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(
        select(Product).where(Product.slug == product_slug, Product.is_active == True, Product.stock > 0))
    if not product:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return product


@router.put('/{product_slug}')
async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct):
    product_update = db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    category = db.scalar(select(Category).where(Category.id == update_product_model.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    db.execute(update(Product).where(Product.slug == product_slug)
               .values(name=update_product_model.name,
                       description=update_product_model.description,
                       price=update_product_model.price,
                       image_url=update_product_model.image_url,
                       stock=update_product_model.stock,
                       category_id=update_product_model.category,
                       slug=slugify(update_product_model.name)))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }

@router.delete('/')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product_delete = db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }