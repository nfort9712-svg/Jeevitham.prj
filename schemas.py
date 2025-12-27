from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from . import models

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_no: Optional[str] = None
    role: models.UserRole = models.UserRole.USER
    status: models.UserStatus = models.UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    role: Optional[models.UserRole] = None
    status: Optional[models.UserStatus] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    status: models.SubscriptionStatus = models.SubscriptionStatus.TRIAL
    auto_renew: bool = True

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[models.SubscriptionStatus] = None
    auto_renew: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    subscriber_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    user_id: int
    subscription_id: Optional[int] = None
    amount: float
    payment_method: models.PaymentMethod
    reference_number: str
    transaction_date: datetime

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    payment_status: Optional[models.PaymentStatus] = None
    amount: Optional[float] = None

class PaymentResponse(PaymentBase):
    payment_id: int
    payment_status: models.PaymentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Ticket Schemas
class TicketBase(BaseModel):
    user_id: int
    subject: str
    description: str
    priority: models.Priority = models.Priority.MEDIUM
    ticket_type: models.TicketType

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[models.TicketStatus] = None
    priority: Optional[models.Priority] = None
    assigned_to: Optional[int] = None

class TicketResponse(TicketBase):
    ticket_id: int
    status: models.TicketStatus
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    user_id: int
    type: models.NotificationType
    notification_category: models.NotificationCategory
    message: str
    priority: models.Priority = models.Priority.MEDIUM

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    status: Optional[models.NotificationStatus] = None

class NotificationResponse(NotificationBase):
    notification_id: int
    status: models.NotificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
