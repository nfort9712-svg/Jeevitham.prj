from sqlalchemy import Column, Integer, String, DateTime, Enum, DECIMAL, Boolean, Text, ForeignKey, DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    USER = "User"
    ADMIN = "Admin"
    SUPPORT = "Support"

class UserStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    BANNED = "Banned"

class PaymentMethod(str, enum.Enum):
    CASH = "Cash"
    UPI = "UPI"
    CHEQUE = "Cheque"
    CARD = "Card"
    PAYPAL = "PayPal"

class PaymentStatus(str, enum.Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class NotificationType(str, enum.Enum):
    EMAIL = "Email"
    SMS = "SMS"
    IN_APP = "In-app"
    PUSH = "Push"

class NotificationCategory(str, enum.Enum):
    SYSTEM = "System"
    MARKETING = "Marketing"
    TRANSACTIONAL = "Transactional"
    SUPPORT = "Support"

class NotificationStatus(str, enum.Enum):
    SEEN = "Seen"
    DELIVERED = "Delivered"
    FAILED = "Failed"

class Priority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"
    CANCELED = "Canceled"
    TRIAL = "Trial"

class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In-progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketType(str, enum.Enum):
    BUG = "Bug"
    FEATURE_REQUEST = "Feature_request"
    SUPPORT = "Support"
    BILLING = "Billing"

# Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_no = Column(String(20))
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    # Relationships
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", foreign_keys="Ticket.user_id", back_populates="user", cascade="all, delete-orphan")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assigned_staff")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    subscriber_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.subscriber_id", ondelete="SET NULL"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    reference_number = Column(String(255), unique=True, nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")


class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    notification_category = Column(Enum(NotificationCategory), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.DELIVERED, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    ticket_type = Column(Enum(TicketType), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    assigned_staff = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
