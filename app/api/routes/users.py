from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, UserType
from app.models.schema import Vendor, VendorUpdate, UserUpdate
from app.services.auth import get_current_user, get_current_vendor
from app.services.users import get_vendor_profile, update_vendor_profile, update_user_gotify_token

router = APIRouter()


@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "user_type": current_user.user_type.value
    }
    return user_data


@router.get("/me/vendor", response_model=Vendor)
async def read_vendor_profile(
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Get vendor profile for current user"""
    vendor_profile = get_vendor_profile(db, current_user.id)
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Combine user and vendor profile data
    return {
        "id": current_user.id,
        "email": current_user.email,
        "user_type": current_user.user_type.value,
        "shop_name": vendor_profile.shop_name,
        "address": vendor_profile.address,
        "shop_type": vendor_profile.shop_type,
        "created_at": current_user.created_at
    }


@router.put("/me/vendor", response_model=Vendor)
async def update_vendor(
    vendor_update: VendorUpdate,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Update vendor profile for current user"""
    updated_profile = update_vendor_profile(db, current_user.id, vendor_update)
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Combine user and updated vendor profile data
    return {
        "id": current_user.id,
        "email": current_user.email,
        "user_type": current_user.user_type.value,
        "shop_name": updated_profile.shop_name,
        "address": updated_profile.address,
        "shop_type": updated_profile.shop_type,
        "created_at": current_user.created_at
    }


@router.put("/me/gotify-token", status_code=status.HTTP_200_OK)
async def update_gotify_token(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update Gotify token for current user"""
    updated_user = update_user_gotify_token(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Gotify token updated successfully"} 