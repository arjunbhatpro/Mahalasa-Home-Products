# ShopHub - Premium E-Commerce Platform

A production-ready full-stack e-commerce application with dual payment options (UPI & Cash on Delivery), real-time order tracking, automated invoice generation, and comprehensive admin management.

## 🚀 Features

### Customer Features
- **Flexible Authentication**: Register/Login via email or phone number
- **Secure Password Recovery**: OTP-based password reset via email or SMS
- **Dual Payment Options**:
  - **UPI Payment**: Scan QR code to pay online
  - **Cash on Delivery (COD)**: Pay when you receive
- **Shopping Experience**:
  - Browse products with real-time stock information
  - Add/remove items from cart
  - Manage quantities with stock validation
- **Order Management**:
  - Real-time order status tracking
  - Automated invoice generation (PDF download)
  - Order history with detailed information
- **Dynamic Status Messages**:
  - UPI: Pending → Paid → Confirmed → Shipped → Delivered
  - COD: Confirmed → Shipped → Delivered

### Admin Features
- **Fixed Admin Login**: Secure admin-only access
- **Product Management**: Add, edit, delete products with stock management
- **User Management**: View and manage customer accounts
- **Order Management**:
  - View all orders across customers
  - Update order status with expected delivery dates
  - Manual payment verification for both UPI and COD
  - Mark COD orders as paid when cash is collected
- **Invoice Management**: Download invoices for any order
- **Dashboard Analytics**: View totals for products, orders, and customers

## 🎨 Design

Premium e-commerce design with "Jewel & Luxury" theme featuring:
- **Colors**: Slate primary, Electric Violet secondary, Emerald accent
- **Typography**: Outfit (headings) + Plus Jakarta Sans (body)
- **Layout**: Responsive grid with modern card design
- **Animations**: Smooth transitions and hover effects

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: Bcrypt for secure password storage
- **PDF Generation**: ReportLab for invoice creation

### Frontend
- **React 19**: Modern React with hooks
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first styling
- **Shadcn/UI**: Premium component library
- **Framer Motion**: Smooth animations
- **Axios**: HTTP client for API calls
- **jsPDF**: Client-side PDF generation
- **Sonner**: Toast notifications

### Integrations (Mock/Demo Mode)
- **PhonePe**: UPI QR code generation and payment verification
- **Twilio**: SMS OTP for phone-based password reset
- **SendGrid**: Email notifications for password reset and order confirmation

## 🔐 Credentials

### Admin Access
- **Email**: `admin@shophub.com`
- **Password**: `admin123`

### Test Customer
You can register a new customer account with:
- Email or phone number (or both)
- Any password you choose

### API Keys (Mock Mode)
All integrations are currently in mock/demo mode with placeholder credentials. OTPs and mock responses are printed in backend logs.

## 🔄 Payment Flows

### UPI (Prepaid) Flow
1. Customer selects "Pay Now (UPI)" at checkout
2. Order created with status "Pending"
3. QR code displayed for payment
4. Payment verified via webhook → Status: "Payment Verified"
5. Invoice automatically generated
6. Admin updates: Confirmed → Shipped → Delivered

### COD (Cash on Delivery) Flow
1. Customer selects "Cash on Delivery" at checkout
2. Order immediately confirmed
3. Payment status: "Pending" (until cash collected)
4. Invoice generated on confirmation
5. Admin ships order
6. Admin marks as "Paid" after cash collection
7. Status: Delivered

## 📱 Key Features

- **Mobile Responsive**: Works perfectly on all devices
- **Real-time Updates**: Order status changes reflect immediately
- **Stock Management**: Automatic stock deduction on order creation
- **PDF Invoices**: Professional invoices with company branding
- **Secure Authentication**: JWT tokens with role-based access
- **Data Validation**: All inputs validated on both frontend and backend

## 🧪 Quick Test Guide
1. **Register**: Create account with email/phone
2. **Shop**: Browse 6 sample products
3. **Checkout**: Try both UPI and COD payment methods
4. **Admin**: Login with admin credentials to manage orders

## 📝 Notes

- This is a **demo/MVP** with mock integrations
- All OTPs are logged to backend console
- Payment webhooks are simulated for demo
- For production: Replace mock API keys with real credentials
- 6 sample products pre-loaded

---

**Built with FastAPI, React, MongoDB, and Tailwind CSS**
