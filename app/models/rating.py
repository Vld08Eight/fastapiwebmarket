from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float  # New
from sqlalchemy.orm import relationship # New

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True)
    grade = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)
    
    reviews = relationship('Review', back_populates='rating')  