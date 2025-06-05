from sqlalchemy.orm import Session
from typing import Optional

from app.models.models import User, VendorProfile, UserType
from app.models.schema import UserCreate, VendorCreate, VendorUpdate, UserUpdate
from app.services.auth import get_password_hash


def create_user(db: Session, user: UserCreate):
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_vendor(db: Session, vendor: VendorCreate):
    """Create a new vendor with profile"""
    # First create the user
    hashed_password = get_password_hash(vendor.password)
    db_user = User(
        email=vendor.email,
        hashed_password=hashed_password,
        user_type=UserType.VENDOR
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Then create the vendor profile
    db_vendor_profile = VendorProfile(
        user_id=db_user.id,
        shop_name=vendor.shop_name,
        address=vendor.address,
        shop_type=vendor.shop_type
    )
    db.add(db_vendor_profile)
    db.commit()
    db.refresh(db_vendor_profile)
    
    return db_user, db_vendor_profile


def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_vendor_profile(db: Session, user_id: int):
    """Get a vendor profile by user ID"""
    return db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()


def update_vendor_profile(db: Session, user_id: int, vendor_update: VendorUpdate):
    """Update a vendor profile"""
    db_vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
    
    if not db_vendor_profile:
        return None
    
    # Update fields if provided
    if vendor_update.shop_name is not None:
        db_vendor_profile.shop_name = vendor_update.shop_name
    
    if vendor_update.address is not None:
        db_vendor_profile.address = vendor_update.address
    
    if vendor_update.shop_type is not None:
        db_vendor_profile.shop_type = vendor_update.shop_type
    
    db.commit()
    db.refresh(db_vendor_profile)
    
    return db_vendor_profile


def update_user_gotify_token(db: Session, user_id: int, user_update: UserUpdate):
    """Update a user's Gotify token"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None
    
    # Update Gotify token if provided
    if user_update.gotify_token is not None:
        db_user.gotify_token = user_update.gotify_token
    
    db.commit()
    db.refresh(db_user)
    
    return db_user 