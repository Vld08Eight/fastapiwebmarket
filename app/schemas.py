from pydantic import BaseModel
from typing import Optional  
class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class  CreateReview(BaseModel):
    header: str
    body: str
    rating: Optional[float] = None
    class Config:
        from_attributes = True
class CreateRating(BaseModel):
    grade: float
