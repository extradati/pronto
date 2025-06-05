from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserType(enum.Enum):
    VENDOR = "vendor"
    CLIENT = "client"

class ItemStatus(enum.Enum):
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COLLECTED = "collected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    user_type = Column(Enum(UserType))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    gotify_token = Column(String, nullable=True)  # Token for Gotify push notifications

    # Relationships
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    items_as_client = relationship("Item", back_populates="client", foreign_keys="Item.client_id")
    notifications = relationship("Notification", back_populates="user")


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    shop_name = Column(String, index=True)
    address = Column(String)
    shop_type = Column(String)

    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    items = relationship("Item", back_populates="vendor")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(String, index=True)
    qr_code = Column(String, unique=True)
    description = Column(Text, nullable=True)
    expected_completion = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.REGISTERED)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"))
    client_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    vendor = relationship("VendorProfile", back_populates="items")
    client = relationship("User", back_populates="items_as_client", foreign_keys=[client_id])
    notifications = relationship("Notification", back_populates="item")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    message = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
    item = relationship("Item", back_populates="notifications") 