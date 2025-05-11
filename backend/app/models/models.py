from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class UserBase(BaseModel):
    email: str
    

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class UserInDB(User):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class CreditCard(BaseModel):
    name: str
    annual_fee: float
    rewards: Dict[str, float]
    welcome_bonus: Optional[Dict[str, Any]] = None


class Spend(BaseModel):
    category: str
    amount: float


class SpendInput(BaseModel):
    spends: List[Spend]


class RecommendationResponse(BaseModel):
    recommended_card: str
    score: float
    comparison: Dict[str, float]


class GmailStatement(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    email_id: str
    subject: str
    from_address: str
    date: datetime
    content: Dict[str, Any]
    created_at: datetime
    
    class Config:
        populate_by_name = True


class UserPreference(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    travel_preference: Optional[int] = None
    cashback_preference: Optional[int] = None
    points_preference: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
