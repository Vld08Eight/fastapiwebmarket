from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert
from slugify import slugify
from sqlalchemy import select, update

from app.backend.db_depends import get_db
from app.schemas import CreateCategory
from app.models.category import Category
from app.models.products import Product



router = APIRouter(prefix='/categories', tags=['category'])



@router.get('/')
async def get_all_categories(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category).where(Category.is_active == True)).all()
    return categories

    
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory):
    # Generate the initial slug from the category name
    slug = slugify(create_category.name)
    
    # Check if the generated slug already exists in the database
    existing_category = db.scalar(select(Category).where(Category.slug == slug))
    
    # If the slug exists, find a unique one by appending a counter
    if existing_category:
        counter = 1
        while True:
            new_slug = f"{slug}-{counter}"
            # Check again with the new slug
            existing = db.scalar(select(Category).where(Category.slug == new_slug))
            if not existing:
                slug = new_slug
                break
            counter += 1
    
    # Insert the new category with the unique slug
    db.execute(
        insert(Category).values(
            name=create_category.name,
            slug=slug,
            parent_id=create_category.parent_id,
            is_active=True  # Explicitly setting is_active (optional if default is set in model)
        )
    )
    db.commit()
    
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.put('/')
async def update_category(db: Annotated[Session, Depends(get_db)], category_id: int, update_category: CreateCategory):
    category = db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )

    db.execute(update(Category).where(Category.id == category_id).values(
            name=update_category.name,
            slug=slugify(update_category.name),
            parent_id=update_category.parent_id))

    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }

@router.delete('/')
async def delete_category(db: Annotated[Session, Depends(get_db)], category_id: int):
    category = db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category delete is successful'
    }