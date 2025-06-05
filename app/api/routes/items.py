from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, ItemStatus
from app.models.schema import Item, ItemCreate, ItemUpdate
from app.services.auth import get_current_user, get_current_vendor
from app.services.items import (
    create_item, get_vendor_items, update_item, update_item_status,
    get_item_by_qr, register_client_for_item
)

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_new_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Create a new item (vendor only)"""
    # Get vendor profile ID
    vendor_profile = current_user.vendor_profile
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Create the item and generate QR code
    db_item, qr_code = create_item(db, item, vendor_profile.id)
    
    return {
        "item": {
            "id": db_item.id,
            "tag_id": db_item.tag_id,
            "description": db_item.description,
            "status": db_item.status.value,
            "created_at": db_item.created_at
        },
        "qr_code": qr_code
    }


@router.get("/", response_model=List[Item])
async def read_vendor_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Get all items for a vendor"""
    # Get vendor profile ID
    vendor_profile = current_user.vendor_profile
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    items = get_vendor_items(db, vendor_profile.id, skip, limit)
    return items


@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Get a specific item by ID (vendor only)"""
    # Get vendor profile ID
    vendor_profile = current_user.vendor_profile
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Get the item
    item = db.query(Item).filter(Item.id == item_id, Item.vendor_id == vendor_profile.id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item_details(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Update an item's details (vendor only)"""
    # Get vendor profile ID
    vendor_profile = current_user.vendor_profile
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Update the item
    updated_item = update_item(db, item_id, item_update, vendor_profile.id)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return updated_item


@router.put("/{item_id}/status", response_model=Item)
async def update_item_status_endpoint(
    item_id: int,
    status: ItemStatus,
    current_user: User = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    """Update an item's status (vendor only)"""
    # Get vendor profile ID
    vendor_profile = current_user.vendor_profile
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Update the item status
    updated_item = update_item_status(db, item_id, status, vendor_profile.id)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return updated_item


@router.post("/scan/{qr_code}", response_model=Item)
async def scan_qr_code(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scan a QR code to register as the client for an item"""
    # Get the item by QR code
    item = get_item_by_qr(db, qr_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found for this QR code"
        )
    
    # Register the client for the item
    updated_item = register_client_for_item(db, qr_code, current_user.id)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register for this item"
        )
    
    return updated_item 