from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, Date # New
from sqlalchemy.orm import relationship # New

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Ссылка на таблицу users
    product_id = Column(Integer, ForeignKey('products.id'))  # Ссылка на таблицу products
    rating_id = Column(Integer, ForeignKey('ratings.id'))  # Ссылка на таблицу ratings
    header = Column(String)
    body = Column(String)
    date = Column(Date)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
    rating = relationship('Rating', back_populates='review')