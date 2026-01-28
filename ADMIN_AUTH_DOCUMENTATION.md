# Admin Authentication Setup - Documentation

## Overview
This document describes the admin authentication system added to the A-Cube Mental Health Platform. The system uses **JWT tokens** for authentication and **bcrypt** for password hashing.

---

## 🎯 What Was Added

### Backend Files Created/Updated

```
/app/backend/
├── api/admin/
│   ├── schemas.py              # Pydantic schemas for admin auth
│   ├── auth.py                 # Authentication logic and JWT handling
│   ├── seed_admin.py           # Script to seed default admin
│   └── admin_router.py         # Updated with protected endpoints
├── requirements.txt            # Updated: added bcrypt>=4.0.0
└── server.py                   # Updated: registered auth router
```

### Frontend Files Created/Updated

```
/app/frontend/src/
├── admin/
│   ├── AdminLogin.tsx          # Login page with form
│   ├── AdminProtectedRoute.tsx # Route protection wrapper
│   └── AdminNavbar.tsx         # Updated: added logout button
└── App.tsx                     # Updated: added login route and protection
```

---

## 🔐 Authentication Flow

### 1. Login Process

```
User enters email & password
        ↓
Frontend sends POST to /api/admin/auth/login
        ↓
Backend verifies credentials (bcrypt)
        ↓
Backend generates JWT token (8 hour expiry)
        ↓
Frontend stores token in localStorage
        ↓
Frontend redirects to /admin
```

### 2. Protected Route Access

```
User navigates to /admin/*
        ↓
AdminProtectedRoute checks for token
        ↓
Sends GET to /api/admin/auth/verify with token
        ↓
Backend validates JWT token
        ↓
If valid: Show admin page
If invalid: Redirect to /admin/login
```

### 3. Logout Process

```
User clicks Logout button
        ↓
Frontend removes token from localStorage
        ↓
Frontend redirects to /admin/login
```

---

## 🔑 Default Admin Credentials

```
Email: admin@acube.com
Password: Admin@2025!
```

**IMPORTANT:** Change this password in production!

---

## 🛠️ Backend Implementation Details

### Password Hashing (bcrypt)

```python
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')
```

### JWT Token Generation

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-secret')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Admin Model

```python
class Admin(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    is_active: bool
```

---

## 📡 API Endpoints

### Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/auth/login` | Admin login |
| GET | `/api/admin/health` | Health check |
| GET | `/api/admin/` | API root |

### Protected Endpoints (Auth Required)

| Method | Endpoint | Description | Header Required |
|--------|----------|-------------|-----------------|
| GET | `/api/admin/auth/verify` | Verify token | `Authorization: Bearer <token>` |
| GET | `/api/admin/stats` | Get dashboard stats | `Authorization: Bearer <token>` |
| GET | `/api/admin/me` | Get current admin info | `Authorization: Bearer <token>` |

---

## 🎨 Frontend Implementation Details

### AdminLogin Component

**Features:**
- Email and password input fields
- Form validation
- Loading state during login
- Error message display
- Professional UI with Tailwind CSS

**Key Code:**
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  const response = await fetch(`${backendUrl}/api/admin/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  localStorage.setItem('admin_token', data.access_token);
  navigate('/admin');
};
```

### AdminProtectedRoute Component

**Features:**
- Checks for token in localStorage
- Verifies token with backend
- Shows loading state during verification
- Redirects to login if unauthenticated
- Renders protected content if authenticated

**Key Code:**
```typescript
const token = localStorage.getItem('admin_token');
const response = await fetch(`${backendUrl}/api/admin/auth/verify`, {
  headers: { 'Authorization': `Bearer ${token}` },
});

if (response.ok) {
  setIsAuthenticated(true);
} else {
  setIsAuthenticated(false);
}
```

### Logout Functionality

**Location:** AdminNavbar component

**Code:**
```typescript
const handleLogout = () => {
  localStorage.removeItem('admin_token');
  navigate('/admin/login');
};
```

---

## 🧪 Testing

### Backend Tests

#### 1. Test Login with Valid Credentials
```bash
curl -X POST http://localhost:8001/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acube.com","password":"Admin@2025!"}'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 2. Test Login with Invalid Credentials
```bash
curl -X POST http://localhost:8001/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acube.com","password":"wrongpassword"}'
```

**Expected Response:**
```json
{
  "detail": "Incorrect email or password"
}
```

#### 3. Test Protected Endpoint Without Token
```bash
curl http://localhost:8001/api/admin/stats
```

**Expected Response:**
```json
{
  "detail": "Not authenticated"
}
```

#### 4. Test Protected Endpoint With Valid Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acube.com","password":"Admin@2025!"}' | \
  jq -r '.access_token')

curl http://localhost:8001/api/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "total_sessions": 0,
  "total_events": 0,
  ...
}
```

#### 5. Test Token Verification
```bash
curl http://localhost:8001/api/admin/auth/verify \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "valid": true,
  "email": "admin@acube.com",
  "id": "..."
}
```

### Frontend Tests

1. Navigate to `/admin` → Should redirect to `/admin/login`
2. Enter wrong credentials → Should show error message
3. Enter correct credentials → Should redirect to `/admin` dashboard
4. Click logout → Should redirect to `/admin/login`
5. Try to access `/admin` after logout → Should redirect to login

---

## 🔒 Security Features

### Implemented

✅ **Password Hashing:** bcrypt with salt  
✅ **JWT Tokens:** 8-hour expiration  
✅ **Token Verification:** Backend validates all requests  
✅ **Protected Routes:** Frontend and backend protection  
✅ **HTTPS Headers:** Proper authentication headers  
✅ **Error Messages:** Generic messages (don't reveal if email exists)

### Not Implemented (By Design)

❌ Refresh tokens  
❌ Role-based access control (RBAC)  
❌ Multi-factor authentication (MFA)  
❌ Password reset functionality  
❌ Account lockout after failed attempts  
❌ Session management  

---

## 🚀 How to Add More Admins

### Method 1: Using Python Script

Create a file `/app/backend/create_admin.py`:

```python
import asyncio
import bcrypt
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def create_admin(email: str, password: str):
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": email,
        "hashed_password": hashed,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.admins.insert_one(admin_data)
    print(f"✅ Admin {email} created!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin("newemail@acube.com", "SecurePassword123!"))
```

Run it:
```bash
cd /app/backend
python create_admin.py
```

### Method 2: Direct MongoDB Insert

```javascript
use acube;  // or your DB name

db.admins.insertOne({
  "id": "new-uuid-here",
  "email": "newemail@acube.com",
  "hashed_password": "$2b$12$hashed_password_here",
  "created_at": new Date(),
  "is_active": true
});
```

---

## 🔍 Troubleshooting

### Issue: Token not working

**Check:**
1. Token stored in localStorage: `localStorage.getItem('admin_token')`
2. Token format: Should start with `eyJ...`
3. Token expiration: Tokens expire after 8 hours
4. Backend SECRET_KEY: Should match between token creation and verification

### Issue: Cannot login

**Check:**
1. Admin exists in database: `db.admins.find()`
2. Password is correct
3. Backend is running: `curl http://localhost:8001/api/admin/health`
4. CORS is configured properly

### Issue: Redirects to login immediately

**Check:**
1. Token verification endpoint is accessible
2. Network tab in browser for failed requests
3. Backend logs for errors: `tail -f /var/log/supervisor/backend.*.log`

---

## 📊 Database Schema

### Collection: `admins`

```json
{
  "_id": ObjectId("..."),
  "id": "uuid-v4-string",
  "email": "admin@acube.com",
  "hashed_password": "$2b$12$...",
  "created_at": ISODate("2024-..."),
  "is_active": true
}
```

**Indexes:**
- Unique index on `email`
- Index on `id`

---

## 🎯 Next Steps (Future Implementation)

When you're ready to enhance the authentication:

1. **Password Management:**
   - Password reset via email
   - Password change functionality
   - Password strength requirements

2. **Security Enhancements:**
   - Refresh tokens
   - Rate limiting on login
   - Account lockout after failed attempts
   - IP-based restrictions

3. **User Management:**
   - Create/edit/delete admins via UI
   - Role-based access control
   - Activity logging

4. **MFA:**
   - TOTP (Google Authenticator)
   - SMS verification
   - Email verification

---

## ✅ Verification Checklist

- [x] Backend authentication endpoints working
- [x] JWT token generation working
- [x] Password hashing with bcrypt
- [x] Default admin seeded
- [x] Login endpoint tested
- [x] Protected endpoints require auth
- [x] Token verification working
- [x] Frontend login page created
- [x] Frontend route protection working
- [x] Logout functionality working
- [x] Existing user-facing features untouched
- [x] All services running without errors

---

## 📞 Quick Reference

### Environment Variables

Add to `/app/backend/.env` (optional):
```
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

### Seed Admin Again

```bash
cd /app/backend
python api/admin/seed_admin.py
```

### Check Admin in Database

```bash
# Via mongo shell
mongo acube --eval "db.admins.find().pretty()"

# Via Python
cd /app/backend
python -c "import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; import os; from dotenv import load_dotenv; load_dotenv('.env'); client = AsyncIOMotorClient(os.environ['MONGO_URL']); async def check(): admins = await client[os.environ['DB_NAME']].admins.find().to_list(10); print(admins); asyncio.run(check())"
```

---

**Document Version:** 1.0  
**Created:** 2024  
**Status:** Authentication Complete ✅  
**User Features:** Untouched ✅
