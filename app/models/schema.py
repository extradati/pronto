from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class UserType(str, Enum):
    VENDOR = "vendor"
    CLIENT = "client"


class ItemStatus(str, Enum):
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COLLECTED = "collected"


class UserBase(BaseModel):
    email: str
    user_type: UserType


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    gotify_token: Optional[str] = None


class VendorCreate(UserCreate):
    shop_name: str
    address: str
    shop_type: str


class VendorUpdate(BaseModel):
    shop_name: Optional[str] = None
    address: Optional[str] = None
    shop_type: Optional[str] = None


class Vendor(UserBase):
    id: int
    shop_name: str
    address: str
    shop_type: str
    created_at: datetime

    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    description: Optional[str] = None
    expected_completion: Optional[datetime] = None


class ItemCreate(ItemBase):
    tag_id: str


class ItemUpdate(BaseModel):
    description: Optional[str] = None
    expected_completion: Optional[datetime] = None
    status: Optional[ItemStatus] = None


class Item(ItemBase):
    id: int
    tag_id: str
    qr_code: str
    vendor_id: int
    client_id: Optional[int] = None
    status: ItemStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    item_id: int
    message: str


class NotificationCreate(NotificationBase):
    pass


class Notification(NotificationBase):
    id: int
    created_at: datetime
    read: bool = False

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    user_type: Optional[UserType] = None


class Token(BaseModel):
    access_token: str
    token_type: str 