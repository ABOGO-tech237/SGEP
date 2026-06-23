"""
# User Types & Creation Guide

## Overview

The SGEP system supports 3 user types (roles):

### 1. **Superadmin** (`superadmin`)
- Full system access
- Can manage schools, teachers, students, parents, and finances
- Can create and manage other administrators
- **Default permissions:** `is_staff=True`, `is_superuser=True`

### 2. **Accountant** (`comptable`)  
- Finance management access
- Can manage fees, invoices, and payments
- Can generate financial reports
- **Restrictions:** No direct student/parent management

### 3. **Parent** (`parent`)
- Limited access to student information
- Can view grades, attendance, and reports for their children
- Can communicate with teachers
- **Restrictions:** Cannot modify student records or manage finances

---

## Account Status

All users have an account status:
- **active**: Account is enabled and can log in
- **suspended**: Account is disabled (prevents login)

---

## Creating Users

### Via API

**Endpoint:** `POST /api/v1/auth/register/`

**Superadmin Creation:**
```json
{
  "email": "admin@sgep.cm",
  "password": "SecurePassword123!",
  "role": "superadmin",
  "account_status": "active"
}
```

**Accountant Creation:**
```json
{
  "email": "accounts@sgep.cm",
  "password": "SecurePassword123!",
  "role": "comptable",
  "account_status": "active"
}
```

**Parent Creation:**
```json
{
  "email": "parent@example.cm",
  "password": "SecurePassword123!",
  "role": "parent",
  "account_status": "active"
}
```

### Via Django Management Command

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create Superadmin
superadmin = User.objects.create_superuser(
    email="admin@sgep.cm",
    password="SecurePassword123!"
)
print(f"Superadmin created: {superadmin.email}")

# Create Accountant
accountant = User.objects.create_user(
    email="accounts@sgep.cm",
    password="SecurePassword123!",
    role="comptable",
    account_status="active"
)
print(f"Accountant created: {accountant.email}")

# Create Parent
parent = User.objects.create_user(
    email="parent@example.cm",
    password="SecurePassword123!",
    role="parent",
    account_status="active"
)
print(f"Parent created: {parent.email}")
```

---

## User Login

**Endpoint:** `POST /api/v1/auth/login/`

**Request:**
```json
{
  "email": "admin@sgep.cm",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Use the `access` token in the `Authorization: Bearer <token>` header for subsequent requests.

---

## User Operations

### Get Current User Info
```bash
GET /api/v1/auth/me/
Authorization: Bearer <access_token>
```

### Change Password
```bash
POST /api/v1/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "CurrentPassword123!",
  "new_password": "NewPassword456!"
}
```

### Logout
```bash
POST /api/v1/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

### Refresh Access Token
```bash
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

## Permission Matrix

| Action | Superadmin | Comptable | Parent |
|--------|-----------|-----------|--------|
| Manage Schools | ✅ | ❌ | ❌ |
| Manage Students | ✅ | ❌ | ❌ |
| Manage Parents | ✅ | ❌ | ❌ |
| Manage Finances | ✅ | ✅ | ❌ |
| View Grades | ✅ | ❌ | ✅ (own children) |
| View Attendance | ✅ | ❌ | ✅ (own children) |
| View Reports | ✅ | ✅ | ✅ (own children) |
| Modify Student Records | ✅ | ❌ | ❌ |

---

## Best Practices

1. **Password Requirements:**
   - Minimum 8 characters
   - Mix of uppercase, lowercase, numbers, and special characters
   - Change default passwords immediately

2. **Account Suspension:**
   - Use `account_status="suspended"` to disable a user without deleting their record
   - Allows re-activation later

3. **Role Assignment:**
   - Assign roles based on responsibilities
   - One user = one primary role
   - Use permissions system for fine-grained access control

4. **Token Management:**
   - Access tokens expire after 15 minutes
   - Use refresh tokens to get new access tokens
   - Implement token rotation for security

---

## Testing

### Unit Tests (Mock-based)
```bash
python manage.py test accounts.tests -v 2
```

### Integration Tests (Real Appwrite Cloud)
```bash
# Make executable
chmod +x run_user_tests.sh

# Run tests
./run_user_tests.sh
```

Or directly:
```bash
python manage.py test accounts.tests_appwrite -v 2
```

### Test Coverage

**Unit Tests (Mock):**
- User creation for all roles
- Password hashing validation
- Duplicate email handling
- User status validation

**Integration Tests (Appwrite Cloud):**
- Real user creation in Appwrite
- Email-based user retrieval
- ID-based user retrieval
- User status updates (active → suspended)
- Case-insensitive email lookup
- Multiple user creation with different roles

### Sample Test Data

```python
# Superadmin
{
    "email": "admin@sgep.test",
    "password": "TestPass123!",
    "role": "superadmin",
    "account_status": "active"
}

# Comptable
{
    "email": "accounts@sgep.test",
    "password": "TestPass123!",
    "role": "comptable",
    "account_status": "active"
}

# Parent
{
    "email": "parent@sgep.test",
    "password": "TestPass123!",
    "role": "parent",
    "account_status": "active"
}
```

"""
