import uuid
import qrcode
import io
import base64
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.models import Item, User, VendorProfile, Notification, ItemStatus, UserType
from app.models.schema import ItemCreate, ItemUpdate
from app.services.notifications import PushNotificationService


def create_qr_code(data: str) -> str:
    """Generate a QR code as a base64 encoded string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def create_item(db: Session, item: ItemCreate, vendor_id: int):
    """Create a new item with a unique QR code"""
    # Generate a unique identifier for the QR code
    unique_id = str(uuid.uuid4())
    
    # Create QR code with the unique ID
    qr_code = create_qr_code(unique_id)
    
    db_item = Item(
        tag_id=item.tag_id,
        qr_code=unique_id,  # Store the ID, not the base64 image
        description=item.description,
        expected_completion=item.expected_completion,
        status=ItemStatus.REGISTERED,
        vendor_id=vendor_id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item, qr_code


def get_item_by_qr(db: Session, qr_code: str):
    """Get an item by its QR code"""
    return db.query(Item).filter(Item.qr_code == qr_code).first()


def get_vendor_items(db: Session, vendor_id: int, skip: int = 0, limit: int = 100):
    """Get all items for a vendor"""
    return db.query(Item).filter(Item.vendor_id == vendor_id).offset(skip).limit(limit).all()


def update_item_status(db: Session, item_id: int, status: ItemStatus, vendor_id: int):
    """Update an item's status"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.vendor_id == vendor_id).first()
    
    if not db_item:
        return None
    
    # Update status
    db_item.status = status
    db_item.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_item)
    
    # If status is completed, create a notification for the client
    if status == ItemStatus.COMPLETED and db_item.client_id:
        # Get client
        client = db.query(User).filter(User.id == db_item.client_id).first()
        
        # Create notification in database
        notification = create_notification(
            db,
            item_id=db_item.id,
            user_id=db_item.client_id,
            message=f"Your item with tag {db_item.tag_id} is ready for collection!"
        )
        
        # Send push notification if client has Gotify token
        if client and client.gotify_token and PushNotificationService.is_initialized():
            try:
                PushNotificationService.send_notification(
                    client_token=client.gotify_token,
                    title="Item Ready for Collection",
                    body=f"Your item with tag {db_item.tag_id} is ready for collection!",
                    data={"item_id": db_item.id, "notification_id": notification.id}
                )
            except Exception as e:
                # Log error but don't fail the status update
                print(f"Failed to send push notification: {e}")
    
    return db_item


def update_item(db: Session, item_id: int, item_update: ItemUpdate, vendor_id: int):
    """Update an item's details"""
    db_item = db.query(Item).filter(Item.id == item_id, Item.vendor_id == vendor_id).first()
    
    if not db_item:
        return None
    
    # Update fields if provided
    if item_update.description is not None:
        db_item.description = item_update.description
    
    if item_update.expected_completion is not None:
        db_item.expected_completion = item_update.expected_completion
    
    if item_update.status is not None:
        db_item.status = item_update.status
        
        # If status is completed, create a notification for the client
        if item_update.status == ItemStatus.COMPLETED and db_item.client_id:
            # Get client
            client = db.query(User).filter(User.id == db_item.client_id).first()
            
            # Create notification in database
            notification = create_notification(
                db,
                item_id=db_item.id,
                user_id=db_item.client_id,
                message=f"Your item with tag {db_item.tag_id} is ready for collection!"
            )
            
            # Send push notification if client has Gotify token
            if client and client.gotify_token and PushNotificationService.is_initialized():
                try:
                    PushNotificationService.send_notification(
                        client_token=client.gotify_token,
                        title="Item Ready for Collection",
                        body=f"Your item with tag {db_item.tag_id} is ready for collection!",
                        data={"item_id": db_item.id, "notification_id": notification.id}
                    )
                except Exception as e:
                    # Log error but don't fail the status update
                    print(f"Failed to send push notification: {e}")
    
    db_item.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_item)
    
    return db_item


def register_client_for_item(db: Session, qr_code: str, user_id: int):
    """Register a client for an item using the QR code"""
    db_item = db.query(Item).filter(Item.qr_code == qr_code).first()
    
    if not db_item:
        return None
    
    # Check if the user exists and is a client
    user = db.query(User).filter(User.id == user_id, User.user_type == UserType.CLIENT).first()
    if not user:
        return None
    
    # Associate the client with the item
    db_item.client_id = user_id
    db.commit()
    db.refresh(db_item)
    
    return db_item


def create_notification(db: Session, item_id: int, user_id: int, message: str):
    """Create a notification for a user"""
    notification = Notification(
        item_id=item_id,
        user_id=user_id,
        message=message
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all notifications for a user"""
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        return None
    
    notification.read = True
    db.commit()
    db.refresh(notification)
    
    return notification 