from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from . import models
from . import schemas

# Database Configuration
# Update these with your MySQL credentials
MYSQL_USER = "root"
MYSQL_PASSWORD = "Chidhu@123"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "project"

# The @ symbol is encoded as %40
DATABASE_URL = "mysql+pymysql://root:Chidhu%40123@localhost:3306/project"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
models.Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="Subscription Management API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_no: Optional[str] = None
    role: models.UserRole = models.UserRole.USER
    status: models.UserStatus = models.UserStatus.ACTIVE

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    role: Optional[models.UserRole] = None
    status: Optional[models.UserStatus] = None

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    phone_no: Optional[str]
    role: models.UserRole
    status: models.UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    status: models.SubscriptionStatus = models.SubscriptionStatus.TRIAL
    auto_renew: bool = True

class SubscriptionUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[models.SubscriptionStatus] = None
    auto_renew: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    subscriber_id: int
    user_id: int
    start_date: date
    end_date: date
    status: models.SubscriptionStatus
    auto_renew: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    user_id: int
    subscription_id: Optional[int] = None
    amount: float
    payment_method: models.PaymentMethod
    reference_number: str
    transaction_date: datetime

class PaymentUpdate(BaseModel):
    payment_status: Optional[models.PaymentStatus] = None
    amount: Optional[float] = None

class PaymentResponse(BaseModel):
    payment_id: int
    user_id: int
    subscription_id: Optional[int]
    amount: float
    payment_method: models.PaymentMethod
    payment_status: models.PaymentStatus
    reference_number: str
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    user_id: int
    subject: str
    description: str
    priority: models.Priority = models.Priority.MEDIUM
    ticket_type: models.TicketType

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[models.TicketStatus] = None
    priority: Optional[models.Priority] = None
    assigned_to: Optional[int] = None

class TicketResponse(BaseModel):
    ticket_id: int
    user_id: int
    subject: str
    description: str
    status: models.TicketStatus
    priority: models.Priority
    ticket_type: models.TicketType
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    user_id: int
    type: models.NotificationType
    notification_category: models.NotificationCategory
    message: str
    priority: models.Priority = models.Priority.MEDIUM

class NotificationUpdate(BaseModel):
    status: Optional[models.NotificationStatus] = None

class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    type: models.NotificationType
    notification_category: models.NotificationCategory
    message: str
    status: models.NotificationStatus
    priority: models.Priority
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API Endpoints

@app.get("/")
def root():
    return {"message": "Subscription Management API", "version": "1.0.0", "status": "running"}

# User Endpoints
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None

# Subscription Endpoints
@app.post("/subscriptions/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == subscription.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_subscription = models.Subscription(**subscription.dict())
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

@app.get("/subscriptions/", response_model=List[SubscriptionResponse])
def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()
    return subscriptions

@app.get("/subscriptions/{subscriber_id}", response_model=SubscriptionResponse)
def get_subscription(subscriber_id: int, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.subscriber_id == subscriber_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@app.get("/subscriptions/user/{user_id}", response_model=List[SubscriptionResponse])
def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).filter(models.Subscription.user_id == user_id).all()
    return subscriptions

@app.put("/subscriptions/{subscriber_id}", response_model=SubscriptionResponse)
def update_subscription(subscriber_id: int, subscription_update: SubscriptionUpdate, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.subscriber_id == subscriber_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    for key, value in subscription_update.dict(exclude_unset=True).items():
        setattr(subscription, key, value)
    
    subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    return subscription

@app.delete("/subscriptions/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscriber_id: int, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription).filter(models.Subscription.subscriber_id == subscriber_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
    return None

# Payment Endpoints
@app.post("/payments/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Check if reference number already exists
    existing_payment = db.query(models.Payment).filter(models.Payment.reference_number == payment.reference_number).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Reference number already exists")
    
    new_payment = models.Payment(**payment.dict(), payment_status=models.PaymentStatus.PENDING)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@app.get("/payments/", response_model=List[PaymentResponse])
def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).offset(skip).limit(limit).all()
    return payments

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/payments/user/{user_id}", response_model=List[PaymentResponse])
def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).filter(models.Payment.user_id == user_id).all()
    return payments

@app.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, payment_update: PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    for key, value in payment_update.dict(exclude_unset=True).items():
        setattr(payment, key, value)
    
    payment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)
    return payment

# Ticket Endpoints
@app.post("/tickets/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = models.Ticket(**ticket.dict())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/tickets/", response_model=List[TicketResponse])
def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).offset(skip).limit(limit).all()
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/tickets/user/{user_id}", response_model=List[TicketResponse])
def get_user_tickets(user_id: int, db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).filter(models.Ticket.user_id == user_id).all()
    return tickets

@app.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    for key, value in ticket_update.dict(exclude_unset=True).items():
        setattr(ticket, key, value)
    
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket

@app.put("/tickets/{ticket_id}/assign/{user_id}", response_model=TicketResponse)
def assign_ticket(ticket_id: int, user_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ticket.assigned_to = user_id
    ticket.status = models.TicketStatus.IN_PROGRESS
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket

@app.put("/tickets/{ticket_id}/close", response_model=TicketResponse)
def close_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = models.TicketStatus.CLOSED
    ticket.ended_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket

# Notification Endpoints
@app.post("/notifications/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    new_notification = models.Notification(**notification.dict())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

@app.get("/notifications/", response_model=List[NotificationResponse])
def get_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).offset(skip).limit(limit).all()
    return notifications

@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.notification_id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.get("/notifications/user/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    return notifications

@app.put("/notifications/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: int, notification_update: NotificationUpdate, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.notification_id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    for key, value in notification_update.dict(exclude_unset=True).items():
        setattr(notification, key, value)
    
    notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

@app.put("/notifications/{notification_id}/mark-seen", response_model=NotificationResponse)
def mark_notification_seen(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(models.Notification.notification_id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = models.NotificationStatus.SEEN
    notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
