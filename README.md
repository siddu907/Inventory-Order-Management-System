# Inventory & Order Management System

A comprehensive **FastAPI-based backend** for managing inventory, orders, payments, and customer relationships. Built with **modern Python technologies** and production-ready features including **JWT authentication with refresh tokens**, **Redis caching**, **coupon system**, and **CSV export capabilities**.

---

## Features

###  **Authentication & Authorization**
- **JWT Tokens**: Access (1-60 min) + Refresh (7 days) tokens
- **Role-Based Access**: Admin, Staff, Customer roles with granular permissions
- **Secure Authentication**: Password hashing with bcrypt, token validation middleware
- **Enhanced Swagger UI**: Automatic token management and session persistence
- **Refresh Token Flow**: Seamless token renewal without re-login

###  **Product & Inventory Management**
- **Product CRUD**: Complete product lifecycle management
- **Category Management**: Hierarchical product categorization
- **SKU Tracking**: Unique product identification
- **Stock Management**: Real-time inventory tracking with min/max levels
- **Low Stock Alerts**: Automated notifications for inventory management
- **Image Uploads**: Product image management with file validation

###  **Order Management**
- **Order Processing**: Complete order lifecycle from creation to delivery
- **Status Tracking**: Pending → Confirmed → Shipped → Delivered → Cancelled
- **Order Items**: Multi-product orders with quantity management
- **Order Validation**: Stock availability and business rule enforcement
- **CSV Export**: Order data export with comprehensive filtering

### **Coupon & Discount System**
- **Coupon Creation**: Percentage-based discount system (Admin only)
- **Usage Tracking**: Automatic usage limit enforcement
- **Expiry Management**: Time-based coupon expiration
- **Order Integration**: Seamless discount application during checkout
- **Case-Insensitive**: Automatic code normalization and lookup

###  **Payment Processing**
- **Payment Simulation**: Complete payment workflow simulation
- **Refund Support**: Administrative refund capabilities
- **Payment Tracking**: Comprehensive payment status management
- **Order Integration**: Automatic payment-order association

###  **Review & Rating System**
- **Customer Reviews**: Product reviews from delivered orders
- **Rating System**: 1-5 star rating with comments
- **Duplicate Prevention**: One review per product per order
- **Review Management**: Customer can update/delete their reviews

### **Notification System**
- **Background Tasks**: APScheduler-based notification processing
- **Event-Driven**: Notifications for orders, payments, stock changes
- **Email Integration**: SMTP-based email notifications
- **Read Status**: Mark notifications as read/unread

###  **Dashboard & Analytics**
- **Role-Specific Dashboards**: Customized views for Admin, Staff, Customer
- **Real-time Metrics**: Order counts, revenue, stock levels
- **Performance Insights**: Business intelligence and reporting

###  **Redis Caching**
- **High-Performance Caching**: Redis-based response caching
- **Smart Invalidation**: Automatic cache updates on data changes
- **Configurable TTL**: Environment-based cache expiration
- **List Endpoint Optimization**: Cached product and category listings

###  **File Management**
- **Image Uploads**: Profile and product image handling
- **File Validation**: Size and format restrictions (max 5MB)
- **Secure Storage**: Organized file structure with validation

---

## Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| **Framework** | FastAPI | 0.115.0 |
| **Language** | Python | 3.11+ |
| **Database** | PostgreSQL | Latest |
| **ORM** | SQLAlchemy | 2.0.35 |
| **Caching** | Redis | Latest |
| **Validation** | Pydantic | 2.9.2 |
| **Migrations** | Alembic | 1.13.0 |
| **Authentication** | python-jose[cryptography] | 3.4.0 |
| **Password Hashing** | passlib[bcrypt] | 1.7.4 |
| **Background Tasks** | APScheduler | 3.10.4 |
| **Testing** | pytest | 8.3.0 |
| **HTTP Client** | httpx | 0.27.0 |
| **Web Server** | uvicorn | 0.30.6 |
| **Database Driver** | psycopg | 3.3.4 |

---

##  Project Architecture

```
 Inventory & Order Management System/
├──  app/
│   ├──  main.py                 # FastAPI app + enhanced Swagger UI
│   ├──  config.py               # Environment configuration
│   ├──  database.py             # SQLAlchemy setup
│   ├──  core/
│   │   ├── constants.py        # Business constants & enums
│   │   ├── dependencies.py     # Dependency injection
│   │   ├── oauth2.py          # JWT token validation
│   │   ├── permissions.py     # Role-based access control
│   │   └── security.py        # Token creation & password hashing
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├──  user.py
│   │   ├──  product.py
│   │   ├──  category.py
│   │   ├──  order.py
│   │   ├──  payment.py
│   │   ├──  coupon.py          # Discount system
│   │   ├──  review.py
│   │   └──  notification.py
│   ├── schemas/                # Pydantic request/response models
│   ├──  repositories/           # Data access layer
│   ├──  services/               # Business logic layer
│   │   ├── cache_service.py   # Redis caching logic
│   │   ├── coupon_service.py  # Coupon validation
│   │   └── auth_service.py    # Authentication logic
│   ├── routers/               # API endpoint definitions
│   ├── background/            # Background task management
│   ├── redis/                 # Redis client configuration
│   └── utils/                 # Utility functions
├── alembic/                   # Database migrations
│   └── versions/
│       ├── 001_initial_inventory.py
│       ├──  002_add_payment_id_to_notifications.py
│       └── 003_add_coupons_and_order_coupon_fields.py
├── .env                       # Environment variables
├── .env.example              # Environment template
├── postman_collection.json   # API testing collection
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Installation & Setup

### **Prerequisites**

Before setting up the project, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis** - [Installation Guide](https://redis.io/docs/getting-started/installation/)

### **Step 1: Python Environment Setup**

```bash
# Check Python version
python --version

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows Command Prompt:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Verify activation 
where python   # Windows
```

### **Step 2: Install Dependencies**

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### **Step 3: Database Setup**

#### **Create Database**

```bash
# Access PostgreSQL as superuser
psql -U postgres

# Inside PostgreSQL shell, create database and user:
CREATE DATABASE inventory_management;
CREATE USER inventory_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_management TO inventory_user;

# Exit PostgreSQL shell
\q
```

### **Step 4: Redis Setup**

#### **Redis Installation**

**Windows:**
```bash
# Option 1: Using Chocolatey
choco install redis-64

# Option 2: Download MSI installer
# Visit: https://github.com/microsoftarchive/redis/releases
# Download and install Redis-x64-x.x.x.msi

# Start Redis service
redis-server

# Or start as Windows service
net start redis
```

#### **Verify Redis Installation**

```bash
# Test Redis connection
redis-cli ping
# Expected output: PONG

# Check Redis version
redis-cli --version
```

### **Step 5: Environment Configuration**

```bash
# Copy environment template
# Windows:
copy .env.example .env

# Edit environment file
# Windows:
notepad .env

**Configure .env file:**
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://inventory_user:your_secure_password@localhost:5432/inventory_management

# Security Settings
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=2

# File Upload Settings
UPLOAD_DIR=app/uploads
MAX_UPLOAD_SIZE=5242880

# Redis Cache Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true
CACHE_TTL=300

# Email Configuration (Optional - Leave blank to disable)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_or_token
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME="Inventory & Order Management"
```
### **Step 6: Database Migration**

```bash
# Check Alembic configuration
alembic current

# Run database migrations to create all tables
alembic upgrade head

# Verify migration success
alembic history --verbose
```

### **Step 7: Run the Application**

```bash
# Start the development server
uvicorn app.main:app --reload

or

python -m uvicorn app.main:app --reload

```

### **Step 8: Access & Test the Application**

#### **Application URLs:**
- **Interactive API Docs**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000

##  API Authentication

### **Authentication Flow**

1. **Register/Login** → Get `access_token` + `refresh_token`
2. **Use API** → Include `Authorization: Bearer {access_token}`
3. **Token Expires** → Use `refresh_token` to get new `access_token`
4. **Automatic Handling** → Swagger UI manages tokens seamlessly

### **Token Configuration**

| Token Type | Default Expiry | Purpose |
|------------|---------------|---------|
| **Access Token** | 24 hours (1440 min) | API access authentication |
| **Refresh Token** | 2 days | Access token renewal |

### **User Roles & Permissions**

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, all CRUD operations |
| **Staff** | Product/inventory management, order processing |
| **Customer** | Place orders, manage profile, write reviews |

---

##  API Endpoints

### **Authentication**
| Method | Endpoint | Description | 
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login | 
| POST | `/auth/refresh` | Refresh access token | 
| GET | `/auth/profile` | Get user profile |
| PUT | `/auth/profile` | Update profile | 
| PUT | `/auth/change-password` | Change password | 

### **Categories**
| Method | Endpoint | Roles | 
|--------|----------|-------|
| POST | `/categories` | Admin |
| GET | `/categories` | Public | 
| GET | `/categories/{id}` | Public | 
| PUT | `/categories/{id}` | Admin | 
| DELETE | `/categories/{id}` | Admin | 

### **Products**
| Method | Endpoint | Roles | 
|--------|----------|-------|
| POST | `/products` | Admin, Staff | 
| GET | `/products` | Public | 
| GET | `/products/{id}` | Public | 
| PUT | `/products/{id}` | Admin, Staff | 
| DELETE | `/products/{id}` | Admin, Staff | 

###  **Inventory**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/inventory` | Create inventory record |
| GET | `/inventory` | List all inventory |
| GET | `/inventory/low-stock` | Get low stock items |
| POST | `/inventory/{id}/add-stock` | Add stock quantity |
| POST | `/inventory/{id}/remove-stock` | Remove stock quantity |

### 🛒 **Orders**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create new order |
| GET | `/orders` | List orders (filtered by role) |
| GET | `/orders/export/csv` | Export orders to CSV |
| GET | `/orders/{id}` | Get order details |
| PUT | `/orders/{id}/confirm` | Confirm order (Admin/Staff) |
| PUT | `/orders/{id}/ship` | Ship order (Admin/Staff) |
| PUT | `/orders/{id}/deliver` | Mark as delivered (Admin/Staff) |
| PUT | `/orders/{id}/cancel` | Cancel order |

### **Coupons**
| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/coupons` | Create coupon | Admin |
| GET | `/coupons` | List coupons | All authenticated |

### **Payments**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments` | Process payment |
| GET | `/payments/{id}` | Get payment details |
| POST | `/payments/{id}/refund` | Refund payment (Admin/Staff) |

### **Reviews**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reviews` | Create product review |
| GET | `/reviews/product/{id}` | Get product reviews |
| PUT | `/reviews/{id}` | Update review (owner only) |
| DELETE | `/reviews/{id}` | Delete review (owner only) |

###  **Notifications**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List user notifications |
| PUT | `/notifications/{id}/read` | Mark notification as read |

###  **Dashboard**
| Method | Endpoint | Description | 
|--------|----------|-------------|
| GET | `/dashboard/admin` | Admin dashboard | 
| GET | `/dashboard/staff` | Staff dashboard | 
| GET | `/dashboard/customer` | Customer dashboard | 

### 📤 **File Uploads**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/uploads/profile-image` | Upload profile picture |
| POST | `/uploads/product-image/{id}` | Upload product image |

---

##  Business Logic & Rules

###  **Inventory Management**
-  Stock levels cannot go negative
-  Automatic low-stock notifications when below minimum threshold
-  Stock validation before order confirmation
-  Real-time stock updates on order processing

###  **Order Processing**
-  **Status Flow**: Pending → Confirmed → Shipped → Delivered
-  **Cancellation**: Only Pending/Confirmed/Shipped orders can be cancelled
-  **Stock Reservation**: Stock is reserved on order creation
- **Total Calculation**: Backend calculates order totals (no client manipulation)

###  **Coupon System**
-  **Percentage Discounts**: 0-100% discount validation
-  **Usage Limits**: Automatic tracking and enforcement
-  **Expiry Management**: Time-based validation
-  **Case Insensitive**: Automatic code normalization

###  **Payment Rules**
-  One payment per order maximum
-  Payments can only be created for confirmed orders
-  Refunds require admin/staff authorization
-  No duplicate refunds allowed

###  **Review System**
-  Only customers with delivered orders can review
-  One review per product per order
-  Reviews can be updated/deleted by owner
-  Rating validation (1-5 stars)

###  **CSV Export**

```bash
# Export orders with advanced filtering:
GET /orders/export/csv?order_status=Pending&start_date=2024-01-01&end_date=2024-12-31

# Includes coupon information:
- Order ID, Customer Details
- Product Information  
- Coupon Code & Discount Amount
- Payment Status & Method
```

### **Background Tasks**

```python
# Automated notifications for:
- Order status changes
- Payment confirmations
- Low stock alerts
- Account activities

# Email integration with:
- SMTP configuration
- Template-based emails  
- Async processing
```

##  Testing

### **Postman Collection**
Import `postman_collection.json` for comprehensive API testing:
-  Complete authentication flow testing
-  Automated token management
-  5-step refresh token workflow validation
-  All endpoint examples with proper headers

### **Manual Testing Steps**

1. **Import Postman collection**
2. **Run "Complete Auth Flow Test"** - Tests full refresh token workflow
3. **Test individual endpoints** - All endpoints have example requests
4. **Verify caching** - Check Redis cache hits in logs

### **Performance Optimization**

- Redis caching for frequently accessed data
- Database query optimization with eager loading
-  Proper indexes on frequently queried columns
-  Background task processing for notifications

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#### **Performance Optimizations:**
- Redis caching for frequently accessed data
- Database query optimization with eager loading
- Proper indexes on frequently queried columns
- Background task processing for notifications
- Connection pooling for database
- Load balancing for high availability




