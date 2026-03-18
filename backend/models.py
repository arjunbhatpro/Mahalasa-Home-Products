from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_VERIFIED = "payment_verified"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class PaymentType(str, Enum):
    UPI = "upi"
    COD = "cod"

# User Models
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: str
    role: UserRole = UserRole.CUSTOMER

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: str
    password: str

class UserLogin(BaseModel):
    identifier: str  # Can be email or phone
    password: str

class ForgotPasswordRequest(BaseModel):
    identifier: str  # email or phone

class ResetPasswordRequest(BaseModel):
    identifier: str
    otp: str
    new_password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    role: str
    created_at: str

# Product Models
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    images: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    images: Optional[List[str]] = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    description: str
    price: float
    stock: int
    images: List[str]
    unit: str = "kg"
    available: bool = True
    coming_soon: bool = False
    weight_options: Optional[List[float]] = None
    piece_options: Optional[List[dict]] = None
    combo_options: Optional[List[int]] = None
    created_at: str
    updated_at: str

# Cart Models
class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartUpdate(BaseModel):
    items: List[CartItem]

class CartResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    items: List[dict]
    updated_at: str

# Order Models
class OrderCreate(BaseModel):
    items: List[CartItem]
    shipping_address: str
    phone: str
    state: str
    payment_type: PaymentType = PaymentType.UPI
    courier_charge: float = 0

class OrderResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    items: List[dict]
    total_amount: float
    shipping_address: str
    phone: str
    state: str
    payment_type: str
    order_status: str
    payment_status: str
    courier_charge: float
    expected_delivery: Optional[str] = None
    created_at: str
    updated_at: str

class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus
    expected_delivery: Optional[str] = None

# Payment Models
class PaymentInitiate(BaseModel):
    order_id: str
    amount: float

class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    qr_code_url: str
    amount: float
    expires_at: str
