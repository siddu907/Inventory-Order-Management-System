# Inventory & Order Management System API Documentation

## Overview

This document provides comprehensive API documentation for the Inventory & Order Management System. The API is built with FastAPI and follows RESTful principles with JWT-based authentication.

**Base URL**: `http://localhost:8000`  
**Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)  
**OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Authentication

### Overview
The API uses JWT (JSON Web Token) authentication with access and refresh tokens:
- **Access Token**: Used for API authentication (expires in 24 hours by default)
- **Refresh Token**: Used to obtain new access tokens (expires in 2 days by default)

### Authentication Flow
1. Register or login to receive both access and refresh tokens
2. Include access token in Authorization header: `Authorization: Bearer {access_token}`
3. When access token expires, use refresh token to get a new access token
4. Swagger UI automatically handles token management and persistence

### User Roles
- **Admin**: Full system access, user management, all CRUD operations
- **Staff**: Product/inventory management, order processing
- **Customer**: Place orders, manage profile, write reviews

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "NewTemp@123",
  "phone": "1234567890",
  "address": "123 Main Street",
  "role": "Customer"
}
```

**Password Requirements:**
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "Customer",
  "phone": "1234567890",
  "address": "123 Main Street",
  "is_active": true
}
```

### POST /auth/login
Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "NewTemp@123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "Customer",
    "phone": "1234567890",
    "address": "123 Main Street",
    "is_active": true
  }
}
```

### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### GET /auth/profile
Get current user profile information.

**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "Customer",
  "phone": "1234567890",
  "address": "123 Main Street",
  "profile_image": "http://localhost:8000/uploads/files/profile_images/user_1.jpg",
  "is_active": true
}
```

### PUT /auth/profile
Update current user profile.

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "full_name": "Updated Name",
  "phone": "9876543210",
  "address": "456 New Street"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "full_name": "Updated Name",
  "role": "Customer",
  "phone": "9876543210",
  "address": "456 New Street",
  "is_active": true
}
```

### PUT /auth/change-password
Change user password.

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "new_password": "NewPassword@456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

## Category Endpoints

### POST /categories
Create a new category.

**Permissions:** Admin only  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "name": "Electronics",
  "description": "Electronic products and accessories",
  "status": "Active"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic products and accessories",
  "status": "Active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### GET /categories
List all categories with optional filtering.

**Query Parameters:**
- `search` (optional): Search by name
- `status` (optional): Filter by status (Active/Inactive)
- `skip` (optional, default=0): Skip records for pagination
- `limit` (optional, default=100): Limit number of records

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic products and accessories",
    "status": "Active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
]
```

### GET /categories/{category_id}
Get a specific category by ID.

**Response (200):**
```json
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic products and accessories",
  "status": "Active",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### PUT /categories/{category_id}
Update a category.

**Permissions:** Admin only  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "name": "Updated Electronics",
  "description": "Updated description",
  "status": "Inactive"
}
```

### DELETE /categories/{category_id}
Delete a category.

**Permissions:** Admin only  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "message": "Category deleted successfully"
}
```

## Product Endpoints

### POST /products
Create a new product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "name": "Smartphone",
  "description": "Latest smartphone with advanced features",
  "category_id": 1,
  "price": 599.99,
  "sku": "PHONE001",
  "stock_quantity": 50,
  "status": "Active"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Smartphone",
  "description": "Latest smartphone with advanced features",
  "category_id": 1,
  "category_name": "Electronics",
  "price": 599.99,
  "sku": "PHONE001",
  "stock_quantity": 50,
  "status": "Active",
  "product_image": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### GET /products
List products with filtering and pagination.

**Query Parameters:**
- `search` (optional): Search by name
- `category_id` (optional): Filter by category
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `status` (optional): Filter by status
- `skip` (optional, default=0): Skip records
- `limit` (optional, default=100): Limit records

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Smartphone",
    "description": "Latest smartphone with advanced features",
    "category_id": 1,
    "category_name": "Electronics",
    "price": 599.99,
    "sku": "PHONE001",
    "stock_quantity": 50,
    "status": "Active",
    "product_image": "http://localhost:8000/uploads/files/product_images/phone001.jpg",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
]
```

### GET /products/{product_id}
Get a specific product by ID.

**Response (200):**
```json
{
  "id": 1,
  "name": "Smartphone",
  "description": "Latest smartphone with advanced features",
  "category_id": 1,
  "category_name": "Electronics",
  "price": 599.99,
  "sku": "PHONE001",
  "stock_quantity": 50,
  "status": "Active",
  "product_image": "http://localhost:8000/uploads/files/product_images/phone001.jpg",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### PUT /products/{product_id}
Update a product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "name": "Updated Smartphone",
  "price": 549.99,
  "stock_quantity": 45
}
```

### DELETE /products/{product_id}
Delete a product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "message": "Product deleted successfully"
}
```

## Inventory Endpoints

### POST /inventory
Create inventory record for a product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "product_id": 1,
  "current_stock": 100,
  "min_stock_level": 10,
  "max_stock_level": 500
}
```

**Response (201):**
```json
{
  "id": 1,
  "product_id": 1,
  "current_stock": 100,
  "min_stock_level": 10,
  "max_stock_level": 500,
  "last_updated": "2024-01-15T10:30:00Z",
  "product_name": "Smartphone",
  "product_sku": "PHONE001",
  "product_status": "Active"
}
```

### GET /inventory
List all inventory records.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100)

### GET /inventory/low-stock
Get products with low stock levels.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
[
  {
    "id": 1,
    "product_id": 1,
    "current_stock": 5,
    "min_stock_level": 10,
    "max_stock_level": 500,
    "last_updated": "2024-01-15T10:30:00Z",
    "product_name": "Smartphone",
    "product_sku": "PHONE001",
    "product_status": "Active"
  }
]
```

### GET /inventory/{product_id}
Get inventory for a specific product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

### POST /inventory/{product_id}/add-stock
Add stock to a product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "quantity": 25
}
```

### POST /inventory/{product_id}/remove-stock
Remove stock from a product.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "quantity": 5
}
```

## Order Endpoints

### POST /orders
Create a new order.

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ],
  "coupon_code": "SAVE10"
}
```

**Response (201):**
```json
{
  "id": 1,
  "customer_id": 1,
  "status": "Pending",
  "total_amount": 1079.98,
  "coupon_code": "SAVE10",
  "discount_amount": 119.98,
  "order_date": "2024-01-15T10:30:00Z",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": 599.99,
      "subtotal": 1199.98
    }
  ],
  "customer": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com"
  }
}
```

### GET /orders
List orders (filtered by user role).

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `order_status` (optional): Filter by status
- `skip` (optional, default=0)
- `limit` (optional, default=100)

**Response (200):**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "status": "Pending",
    "total_amount": 1079.98,
    "coupon_code": "SAVE10",
    "discount_amount": 119.98,
    "order_date": "2024-01-15T10:30:00Z",
    "items": [...],
    "customer": {...}
  }
]
```

### GET /orders/export/csv
Export orders to CSV format.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `order_status` (optional): Pending, Confirmed, Shipped, Delivered, Cancelled

**Response:** CSV file download with columns:
- Order ID, Customer ID, Customer Name, Customer Email
- Order Date, Order Status, Product Name, SKU
- Quantity, Unit Price, Item Subtotal
- Coupon Code, Discount Amount, Order Total
- Payment Status, Payment Method

### GET /orders/{order_id}
Get specific order details.

**Headers:** `Authorization: Bearer {access_token}`

### PUT /orders/{order_id}/confirm
Confirm an order (change status to Confirmed).

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

### PUT /orders/{order_id}/ship
Ship an order (change status to Shipped).

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

### PUT /orders/{order_id}/deliver
Mark order as delivered.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

### PUT /orders/{order_id}/cancel
Cancel an order.

**Headers:** `Authorization: Bearer {access_token}`

## Coupon Endpoints

### POST /coupons
Create a new coupon.

**Permissions:** Admin only  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "code": "SAVE20",
  "description": "20% discount on all products",
  "discount_percent": 20.0,
  "expires_at": "2024-12-31T23:59:59Z",
  "usage_limit": 100
}
```

**Response (201):**
```json
{
  "id": 1,
  "code": "SAVE20",
  "description": "20% discount on all products",
  "discount_percent": 20.0,
  "expires_at": "2024-12-31T23:59:59Z",
  "is_active": true,
  "usage_limit": 100,
  "used_count": 0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /coupons
List all coupons.

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100)

## Payment Endpoints

### POST /payments
Process payment for an order.

**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "order_id": 1,
  "payment_method": "Credit Card"
}
```

**Response (201):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 1079.98,
  "payment_method": "Credit Card",
  "status": "Completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /payments/{payment_id}
Get payment details.

**Headers:** `Authorization: Bearer {access_token}`

### POST /payments/{payment_id}/refund
Refund a payment.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "id": 1,
  "order_id": 1,
  "amount": 1079.98,
  "payment_method": "Credit Card",
  "status": "Refunded",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Review Endpoints

### POST /reviews
Create a product review.

**Permissions:** Customer only (must have delivered order)  
**Headers:** `Authorization: Bearer {access_token}`

**Request Body:**
```json
{
  "product_id": 1,
  "order_id": 1,
  "rating": 5,
  "review": "Excellent product, highly recommended!"
}
```

**Response (201):**
```json
{
  "id": 1,
  "product_id": 1,
  "customer_id": 1,
  "order_id": 1,
  "rating": 5,
  "review": "Excellent product, highly recommended!",
  "created_at": "2024-01-15T10:30:00Z",
  "customer_name": "John Doe",
  "product_name": "Smartphone"
}
```

### GET /reviews/product/{product_id}
Get all reviews for a product.

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100)

### PUT /reviews/{review_id}
Update a review (owner only).

**Permissions:** Customer (review owner)  
**Headers:** `Authorization: Bearer {access_token}`

### DELETE /reviews/{review_id}
Delete a review (owner only).

**Permissions:** Customer (review owner)  
**Headers:** `Authorization: Bearer {access_token}`

## Notification Endpoints

### GET /notifications
Get user notifications.

**Headers:** `Authorization: Bearer {access_token}`

**Query Parameters:**
- `skip` (optional, default=0)
- `limit` (optional, default=100)

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Order Confirmed",
    "message": "Your order #1 has been confirmed",
    "is_read": false,
    "created_at": "2024-01-15T10:30:00Z",
    "notification_type": "order_confirmed",
    "order_id": 1
  }
]
```

### PUT /notifications/{notification_id}/read
Mark notification as read.

**Headers:** `Authorization: Bearer {access_token}`

## Dashboard Endpoints

### GET /dashboard/admin
Get admin dashboard statistics.

**Permissions:** Admin only  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "total_orders": 150,
  "total_revenue": 45678.90,
  "total_customers": 25,
  "total_products": 50,
  "pending_orders": 12,
  "low_stock_products": 3,
  "recent_orders": [...],
  "top_products": [...]
}
```

### GET /dashboard/staff
Get staff dashboard statistics.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

### GET /dashboard/customer
Get customer dashboard statistics.

**Permissions:** Customer  
**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "total_orders": 5,
  "total_spent": 2399.95,
  "recent_orders": [...],
  "favorite_products": [...]
}
```

## File Upload Endpoints

### POST /uploads/profile-image
Upload profile image.

**Headers:** `Authorization: Bearer {access_token}`

**Request:** `multipart/form-data`
- `file`: Image file (JPEG, PNG, JPG, WebP, max 5MB)

**Response (200):**
```json
{
  "message": "Profile image uploaded successfully",
  "path": "/uploads/profile_images/user_1.jpg",
  "url": "http://localhost:8000/uploads/files/profile_images/user_1.jpg"
}
```

### POST /uploads/product-image/{product_id}
Upload product image.

**Permissions:** Admin, Staff  
**Headers:** `Authorization: Bearer {access_token}`

**Request:** `multipart/form-data`
- `file`: Image file (JPEG, PNG, JPG, WebP, max 5MB)

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created successfully
- `400` - Bad Request (validation error, invalid input)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate resource)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Validation Errors
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 characters",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

## Rate Limiting and Caching

### Redis Caching
- Product listings cached for 5 minutes
- Category listings cached for 5 minutes
- Dashboard data cached for 1-2 minutes
- Individual records cached for 5 minutes
- Automatic cache invalidation on data changes

### Performance Features
- Database query optimization with eager loading
- Background task processing for notifications
- Efficient pagination with skip/limit parameters
- File upload validation and size limits

## Development and Testing

### Testing with Postman
1. Import the provided `postman_collection.json`
2. The collection includes comprehensive authentication flow testing
3. Automated token management and refresh workflows
4. Example requests for all endpoints

### Environment Variables
Required environment variables for development:
```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/inventory_management
SECRET_KEY=change-me-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=2
REDIS_ENABLED=true
CACHE_TTL=5
```

### Database Setup
1. Create PostgreSQL database: `inventory_management`
2. Run migrations: `alembic upgrade head`
3. Start Redis server for caching functionality

### Production Considerations
- Reduce access token expiry to 15-30 minutes for production
- Enable HTTPS for secure token transmission
- Configure proper CORS settings
- Set up proper logging and monitoring
- Use environment-specific configuration files