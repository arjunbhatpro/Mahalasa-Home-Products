from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid
from typing import List, Optional
import io

from models import *
from auth import *
from integrations import twilio_service, sendgrid_service, phonepe_service
from invoice_generator import generate_invoice_pdf

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="ShopHub E-Commerce API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== AUTHENTICATION ROUTES ====================

@api_router.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new customer"""
    # Validate that at least email or phone is provided
    if not user_data.email and not user_data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or phone is required"
        )
    
    # Check if user already exists
    query = {}
    if user_data.email:
        query["email"] = user_data.email
    if user_data.phone:
        if query:
            query = {"$or": [{"email": user_data.email}, {"phone": user_data.phone}]}
        else:
            query["phone"] = user_data.phone
    
    existing_user = await db.users.find_one(query, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create user
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "phone": user_data.phone,
        "name": user_data.name,
        "role": "customer",
        "password": get_password_hash(user_data.password),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_dict["id"], "role": user_dict["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_dict["id"],
            "name": user_dict["name"],
            "email": user_dict["email"],
            "phone": user_dict["phone"],
            "role": user_dict["role"]
        }
    }

@api_router.post("/auth/login", response_model=dict)
async def login(credentials: UserLogin):
    """Login with email or phone"""
    # Find user by email or phone
    query = {"$or": [
        {"email": credentials.identifier},
        {"phone": credentials.identifier}
    ]}
    
    user = await db.users.find_one(query, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["id"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user.get("email"),
            "phone": user.get("phone"),
            "role": user["role"]
        }
    }

@api_router.post("/auth/admin-login", response_model=dict)
async def admin_login(credentials: UserLogin):
    """Fixed admin login"""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@shophub.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    if credentials.identifier != admin_email or credentials.password != admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    
    # Check if admin user exists in DB, if not create
    admin = await db.users.find_one({"email": admin_email, "role": "admin"}, {"_id": 0})
    if not admin:
        admin = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "name": "Admin",
            "role": "admin",
            "password": get_password_hash(admin_password),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": admin["id"], "role": "admin"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin["id"],
            "name": admin["name"],
            "email": admin["email"],
            "role": "admin"
        }
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset OTP"""
    identifier = request.identifier
    
    # Check if it's email or phone
    is_email = "@" in identifier
    
    query = {"email": identifier} if is_email else {"phone": identifier}
    user = await db.users.find_one(query, {"_id": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Send OTP
    if is_email:
        await sendgrid_service.send_reset_email(identifier, "reset_token")
    else:
        await twilio_service.send_otp(identifier)
    
    return {"message": "OTP sent successfully", "type": "email" if is_email else "phone"}

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with OTP"""
    identifier = request.identifier
    is_email = "@" in identifier
    
    # Verify OTP
    if is_email:
        verified = await sendgrid_service.verify_otp(identifier, request.otp)
    else:
        verified = await twilio_service.verify_otp(identifier, request.otp)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Update password
    query = {"email": identifier} if is_email else {"phone": identifier}
    result = await db.users.update_one(
        query,
        {"$set": {"password": get_password_hash(request.new_password)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Password reset successful"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ==================== PRODUCT ROUTES ====================

@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(skip: int = 0, limit: int = 100):
    """Get all products"""
    products = await db.products.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return products

@api_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get single product"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, admin: dict = Depends(get_admin_user)):
    """Create new product (admin only)"""
    product_dict = product.model_dump()
    product_dict["id"] = str(uuid.uuid4())
    product_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    product_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.products.insert_one(product_dict)
    return product_dict

@api_router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate, admin: dict = Depends(get_admin_user)):
    """Update product (admin only)"""
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.products.update_one(
        {"id": product_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    return product

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin: dict = Depends(get_admin_user)):
    """Delete product (admin only)"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# ==================== CART ROUTES ====================

@api_router.get("/cart")
async def get_cart(current_user: dict = Depends(get_current_user)):
    """Get user's cart"""
    cart = await db.carts.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not cart:
        return {"user_id": current_user["id"], "items": [], "updated_at": datetime.now(timezone.utc).isoformat()}
    
    # Populate product details
    items_with_details = []
    for item in cart.get("items", []):
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        if product:
            items_with_details.append({
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "product": product
            })
    
    cart["items"] = items_with_details
    return cart

@api_router.post("/cart")
async def update_cart(cart_update: CartUpdate, current_user: dict = Depends(get_current_user)):
    """Update user's cart"""
    cart_dict = {
        "user_id": current_user["id"],
        "items": [item.model_dump() for item in cart_update.items],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.carts.update_one(
        {"user_id": current_user["id"]},
        {"$set": cart_dict},
        upsert=True
    )
    
    return {"message": "Cart updated successfully"}

@api_router.delete("/cart")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """Clear user's cart"""
    await db.carts.delete_one({"user_id": current_user["id"]})
    return {"message": "Cart cleared successfully"}

@api_router.post("/orders/calculate-courier")
async def calculate_courier(request: dict):
    """Calculate courier charges based on state and cart items"""
    state = request.get("state", "")
    cart_items = request.get("items", [])
    subtotal = request.get("subtotal", 0)
    
    courier_charge = 0
    
    # Karnataka + total < 350 → ₹30
    if state == "Karnataka" and subtotal < 350:
        courier_charge = 30
    
    # Outside Karnataka: calculate based on items
    elif state != "Karnataka":
        for item in cart_items:
            quantity = item.get("quantity", 0)
            product_name = item.get("product_name", "")
            
            if quantity <= 0:
                continue
            
            # Papad products have different courier charges
            if "Papad" in product_name:
                pieces = quantity  # Assuming quantity represents pieces for papad
                if pieces <= 50:
                    courier_charge += 20
                elif pieces <= 100:
                    courier_charge += 30
                else:
                    courier_charge += 40
            else:
                # Regular products: ₹50 per kg/unit
                courier_charge += quantity * 50
    
    return {
        "courier_charge": courier_charge,
        "subtotal": subtotal,
        "total": subtotal + courier_charge
    }

# ==================== ORDER ROUTES ====================

@api_router.get("/orders", response_model=List[OrderResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    """Get user's orders"""
    query = {} if current_user["role"] == "admin" else {"user_id": current_user["id"]}
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get single order"""
    query = {"id": order_id}
    if current_user["role"] != "admin":
        query["user_id"] = current_user["id"]
    
    order = await db.orders.find_one(query, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@api_router.post("/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Create new order"""
    # Calculate total and get product details
    items_with_details = []
    total_amount = 0
    
    for item in order_data.items:
        product = await db.products.find_one({"id": item.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        # Calculate price based on product type
        item_price = product["price"]
        
        # For piece-based products, find the correct price tier
        if product.get("piece_options"):
            for option in product["piece_options"]:
                if option["pieces"] == item.quantity:
                    item_price = option["price"] / option["pieces"]  # Price per piece
                    break
        
        item_total = item_price * item.quantity
        total_amount += item_total
        
        items_with_details.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "price": item_price,
            "unit": product.get("unit", "unit")
        })
    
    # Determine order status based on payment type
    payment_type = order_data.payment_type.value
    
    if payment_type == "cod":
        # COD orders are immediately confirmed, payment pending until delivery
        order_status = "confirmed"
        payment_status = "pending"
    else:
        # UPI orders remain pending until payment
        order_status = "pending"
        payment_status = "pending"
    
    # Create order
    order_dict = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "items": items_with_details,
        "total_amount": total_amount,
        "shipping_address": order_data.shipping_address,
        "phone": order_data.phone,
        "state": order_data.state,
        "courier_charge": order_data.courier_charge,
        "payment_type": payment_type,
        "order_status": order_status,
        "payment_status": payment_status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.orders.insert_one(order_dict)
    
    # Update product stock
    for item in order_data.items:
        await db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"stock": -item.quantity}}
        )
    
    # Clear cart after order creation
    await db.carts.delete_one({"user_id": current_user["id"]})
    
    # For COD, send order confirmation email immediately
    if payment_type == "cod":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if user and user.get("email"):
            await sendgrid_service.send_order_confirmation(
                user["email"],
                order_dict["id"],
                order_dict["total_amount"]
            )
    
    return order_dict

@api_router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str, 
    status_update: OrderStatusUpdate, 
    admin: dict = Depends(get_admin_user)
):
    """Update order status (admin only)"""
    update_data = {
        "order_status": status_update.order_status.value,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if status_update.expected_delivery:
        update_data["expected_delivery"] = status_update.expected_delivery
    
    result = await db.orders.update_one(
        {"id": order_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated successfully"}

# ==================== PAYMENT ROUTES ====================

@api_router.post("/payments/initiate", response_model=PaymentResponse)
async def initiate_payment(payment: PaymentInitiate, current_user: dict = Depends(get_current_user)):
    """Initiate payment for an order (UPI only)"""
    # Verify order exists and belongs to user
    query = {"id": payment.order_id}
    if current_user["role"] != "admin":
        query["user_id"] = current_user["id"]
    
    order = await db.orders.find_one(query, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order is COD
    if order.get("payment_type") == "cod":
        raise HTTPException(status_code=400, detail="Payment not required for Cash on Delivery orders")
    
    if order["payment_status"] == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    # Generate QR code
    qr_response = await phonepe_service.generate_qr_code(payment.order_id, payment.amount)
    
    # Store payment record
    payment_dict = {
        "id": str(uuid.uuid4()),
        "order_id": payment.order_id,
        "transaction_id": qr_response["transaction_id"],
        "amount": payment.amount,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payments.insert_one(payment_dict)
    
    return qr_response

@api_router.post("/payments/webhook")
async def payment_webhook(webhook_data: dict):
    """Handle payment webhook from PhonePe"""
    logger.info(f"Payment webhook received: {webhook_data}")
    
    transaction_id = webhook_data.get("transaction_id")
    status = webhook_data.get("status", "failed")
    
    # Update payment status
    await db.payments.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Update order payment status
    payment = await db.payments.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if payment:
        await db.orders.update_one(
            {"id": payment["order_id"]},
            {"$set": {
                "payment_status": "paid" if status == "success" else "failed",
                "order_status": "payment_verified" if status == "success" else "pending",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Send confirmation email
        order = await db.orders.find_one({"id": payment["order_id"]}, {"_id": 0})
        if order and status == "success":
            user = await db.users.find_one({"id": order["user_id"]}, {"_id": 0})
            if user and user.get("email"):
                await sendgrid_service.send_order_confirmation(
                    user["email"],
                    order["id"],
                    order["total_amount"]
                )
    
    return {"status": "received"}

@api_router.post("/payments/verify/{order_id}")
async def verify_payment_manual(order_id: str, admin: dict = Depends(get_admin_user)):
    """Manually verify payment (admin only) - for both UPI and COD"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    result = await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "payment_status": "paid",
            "order_status": "payment_verified" if order.get("payment_type") == "upi" else "confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Payment verified successfully"}

@api_router.post("/orders/{order_id}/mark-paid")
async def mark_cod_paid(order_id: str, admin: dict = Depends(get_admin_user)):
    """Mark COD order as paid when cash is collected (admin only)"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.get("payment_type") != "cod":
        raise HTTPException(status_code=400, detail="This endpoint is only for COD orders")
    
    result = await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "payment_status": "paid",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "Order marked as paid successfully"}

# ==================== INVOICE ROUTES ====================

@api_router.get("/orders/{order_id}/invoice")
async def download_invoice(order_id: str, current_user: dict = Depends(get_current_user)):
    """Download invoice PDF"""
    query = {"id": order_id}
    if current_user["role"] != "admin":
        query["user_id"] = current_user["id"]
    
    order = await db.orders.find_one(query, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get user details
    user = await db.users.find_one({"id": order["user_id"]}, {"_id": 0})
    
    # Prepare invoice data
    invoice_data = {
        "id": order["id"],
        "created_at": order["created_at"],
        "payment_status": order["payment_status"],
        "order_status": order["order_status"],
        "customer_name": user.get("name", "N/A"),
        "customer_email": user.get("email", "N/A"),
        "phone": order.get("phone", "N/A"),
        "shipping_address": order.get("shipping_address", "N/A"),
        "items": order["items"],
        "total_amount": order["total_amount"],
        "expected_delivery": order.get("expected_delivery")
    }
    
    # Generate PDF
    pdf_bytes = generate_invoice_pdf(invoice_data)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{order_id}.pdf"}
    )

# ==================== ADMIN USER MANAGEMENT ====================

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(admin: dict = Depends(get_admin_user)):
    """Get all users (admin only)"""
    users = await db.users.find({"role": "customer"}, {"_id": 0, "password": 0}).to_list(1000)
    return users

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    """Delete user (admin only)"""
    result = await db.users.delete_one({"id": user_id, "role": "customer"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@api_router.delete("/admin/orders/{order_id}")
async def delete_old_order(order_id: str, admin: dict = Depends(get_admin_user)):
    """Delete old order for privacy (admin only)"""
    result = await db.orders.delete_one({"id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

# ==================== HEALTH CHECK ====================

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "shophub-api"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
