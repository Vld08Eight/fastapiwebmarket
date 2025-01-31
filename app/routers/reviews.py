from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from sqlalchemy import func

from app.backend.db_depends import get_db
from app.schemas import CreateReview
from app.models import *
from app.models.category import Category
from app.models.user import User
from app.models.product import Product
from app.models.review import Review
from app.routers.auth import get_current_user

router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get("/")
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if reviews is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return reviews.all()

@router.get("/{product_slug}")
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    reviews = await db.scalars(select(Review).where(Review.product_id == Product.id))
    if reviews is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return reviews.all()

@router.post("/{product_id}")
async def add_review(
    db: Annotated[AsyncSession, Depends(get_db)], 
    product_id: int, 
    create_review: CreateReview,
    get_user: Annotated[dict, Depends(get_current_user)]
):
    # Validate user
    user = await db.scalar(select(User).where(User.id == get_user.get('id')))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required"
        )
    
    # Verify product exists
    product = await db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.is_active == True
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Create review
    review_data = {
        "user_id": get_user['id'],
        "product_id": product_id,
        "header": create_review.header,
        "body": create_review.body
    }
    if create_review.rating:
        rating = Rating(
            grade=create_review.rating,
            user_id=get_user['id'],
            product_id=product_id
        )
        db.add(rating)
        await db.flush()
        review_data["rating_id"] = rating.id

        # Обновляем средний рейтинг продукта
        new_avg = await db.scalar(
            select(func.avg(Rating.grade)).where(
                Rating.product_id == product_id
            )
        )
        product.rating = new_avg
    
    # Create rating if provided
    if create_review.rating:
        rating = Rating(
            grade=create_review.rating,
            user_id=get_user['id'],
            product_id=product_id
        )
        db.add(rating)
        await db.flush()  # Get rating ID
        review_data["rating_id"] = rating.id
    
    # Create review
    review = Review(**review_data)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return review

@router.delete("/{product_id}")
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], product_id: int):
    if get_user.get('is_admin'):    

        result_review = await db.execute(
            update(Review)
            .where(Review.product_id == product_id)
            .values(is_active=False)
        )
        if result_review.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no reviews found'
            )


        result_rating = await db.execute(
            update(Rating)
            .where(Rating.product_id == product_id)
            .values(is_active=False)
        )
        if result_rating.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no ratings found'
            )
        product = await db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(rating = 0)
        )
        if product.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        await db.commit()

        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Reviews delete is successful'
        }