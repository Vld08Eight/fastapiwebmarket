from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, Date # New
from sqlalchemy.orm import relationship # New
from sqlalchemy import func  # Add this import

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('ratings.id'), nullable=True)  # Single definition
    header = Column(String)
    body = Column(String)
    date = Column(Date, default=func.now())  # Add default
    is_active = Column(Boolean, default=True)
    
    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
    rating = relationship('Rating', back_populates='reviews')  # Correct relationship