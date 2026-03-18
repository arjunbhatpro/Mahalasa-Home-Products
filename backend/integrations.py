import os
import random
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Mock OTP storage (in production, use Redis or database)
otp_storage = {}

class TwilioService:
    """Mock Twilio service for SMS OTP"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "MOCK_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "MOCK_AUTH_TOKEN")
        self.verify_service = os.getenv("TWILIO_VERIFY_SERVICE", "MOCK_VERIFY_SERVICE")
    
    async def send_otp(self, phone: str) -> bool:
        """Send OTP via SMS (mocked)"""
        otp = ''.join(random.choices(string.digits, k=6))
        otp_storage[phone] = {
            'otp': otp,
            'expires': datetime.now() + timedelta(minutes=15)
        }
        logger.info(f"[MOCK SMS] OTP sent to {phone}: {otp}")
        print(f"\n=== MOCK SMS OTP ===")
        print(f"Phone: {phone}")
        print(f"OTP: {otp}")
        print(f"Expires in 15 minutes\n")
        return True
    
    async def verify_otp(self, phone: str, otp: str) -> bool:
        """Verify OTP (mocked)"""
        stored = otp_storage.get(phone)
        if not stored:
            return False
        if datetime.now() > stored['expires']:
            del otp_storage[phone]
            return False
        if stored['otp'] == otp:
            del otp_storage[phone]
            return True
        return False

class SendGridService:
    """Mock SendGrid service for emails"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY", "MOCK_SENDGRID_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@shopapp.com")
    
    async def send_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email (mocked)"""
        otp = ''.join(random.choices(string.digits, k=6))
        otp_storage[email] = {
            'otp': otp,
            'expires': datetime.now() + timedelta(minutes=15)
        }
        logger.info(f"[MOCK EMAIL] Reset OTP sent to {email}: {otp}")
        print(f"\n=== MOCK EMAIL OTP ===")
        print(f"To: {email}")
        print(f"Subject: Password Reset OTP")
        print(f"OTP: {otp}")
        print(f"Expires in 15 minutes\n")
        return True
    
    async def verify_otp(self, email: str, otp: str) -> bool:
        """Verify email OTP (mocked)"""
        stored = otp_storage.get(email)
        if not stored:
            return False
        if datetime.now() > stored['expires']:
            del otp_storage[email]
            return False
        if stored['otp'] == otp:
            del otp_storage[email]
            return True
        return False
    
    async def send_order_confirmation(self, email: str, order_id: str, total: float) -> bool:
        """Send order confirmation email (mocked)"""
        logger.info(f"[MOCK EMAIL] Order confirmation sent to {email} for order {order_id}")
        print(f"\n=== MOCK ORDER CONFIRMATION EMAIL ===")
        print(f"To: {email}")
        print(f"Subject: Order Confirmation - {order_id}")
        print(f"Total: ₹{total}\n")
        return True

class PhonePeService:
    """Mock PhonePe service for UPI payments"""
    
    def __init__(self):
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID", "MOCK_MERCHANT")
        self.client_id = os.getenv("PHONEPE_CLIENT_ID", "MOCK_CLIENT_ID")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY", "MOCK_SALT_KEY")
    
    async def generate_qr_code(self, order_id: str, amount: float) -> dict:
        """Generate UPI QR code (mocked)"""
        transaction_id = f"TXN_{order_id}_{random.randint(100000, 999999)}"
        expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()
        
        # Mock QR code URL (in production, this would be from PhonePe API)
        qr_code_url = f"https://api.phonepe.com/qr/{transaction_id}"
        
        logger.info(f"[MOCK PHONEPE] QR generated for order {order_id}: {transaction_id}")
        print(f"\n=== MOCK PHONEPE QR CODE ===")
        print(f"Order ID: {order_id}")
        print(f"Transaction ID: {transaction_id}")
        print(f"Amount: ₹{amount}")
        print(f"QR URL: {qr_code_url}")
        print(f"Scan with any UPI app to pay (MOCKED)\n")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "qr_code_url": qr_code_url,
            "amount": amount,
            "expires_at": expires_at
        }
    
    async def verify_payment(self, transaction_id: str) -> bool:
        """Verify payment status (mocked - always returns True for demo)"""
        logger.info(f"[MOCK PHONEPE] Payment verified for transaction {transaction_id}")
        return True

# Service instances
twilio_service = TwilioService()
sendgrid_service = SendGridService()
phonepe_service = PhonePeService()
