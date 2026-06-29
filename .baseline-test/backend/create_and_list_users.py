"""Create new users and retrieve users & auth accounts."""

import os
import sys
from pathlib import Path
from datetime import datetime
import requests

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from config.appwrite_client import users
from accounts.repository import UserRepository
from accounts.models import ROLE_SUPERADMIN, ROLE_COMPTABLE, ROLE_PARENT, ACCOUNT_STATUS_ACTIVE
from appwrite.exception import AppwriteException
from django.conf import settings

# Appwrite API config
ENDPOINT = settings.APPWRITE_ENDPOINT.rstrip('/v1')
DB_ID = settings.APPWRITE_DB_ID
PROJECT_ID = settings.APPWRITE_PROJECT_ID
API_KEY = settings.APPWRITE_API_KEY
USERS_COLLECTION = "users"

API_HEADERS = {
    "X-Appwrite-Project": PROJECT_ID,
    "X-Appwrite-Key": API_KEY,
}

print("=" * 70)
print("CREATE NEW USERS & RETRIEVE LISTS")
print("=" * 70)

# ==================== 1. CREATE NEW USERS ====================
print("\n📝 STEP 1: Creating new users...")
print("-" * 70)

new_users = [
    {
        "email": "superadmin2@sgep.cm",
        "first_name": "Admin",
        "last_name": "Secondaire",
        "role": ROLE_SUPERADMIN,
        "password": "SuperAdmin123!",
        "description": "Super Admin 2"
    },
    {
        "email": "comptable2@sgep.cm",
        "first_name": "Comptable",
        "last_name": "Secondaire",
        "role": ROLE_COMPTABLE,
        "password": "Comptable123!",
        "description": "Comptable 2"
    },
    {
        "email": "directeur@sgep.cm",
        "first_name": "Pierre",
        "last_name": "Directeur",
        "role": "directeur",
        "password": "DirecteurPassword123!",
        "description": "School Director"
    }
]

created_users = []

for user_info in new_users:
    email = user_info["email"]
    password = user_info.pop("password")
    description = user_info.pop("description")

    print(f"\n📌 Creating: {description}")
    print(f"   Email: {email}")

    try:
        # 1. Create document in Users collection (WITHOUT password field)
        now = datetime.utcnow().isoformat()
        user_data = {
            "email": email.lower(),
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "role": user_info["role"],
            "account_status": ACCOUNT_STATUS_ACTIVE,
            "created_at": now,
            "updated_at": now,
        }
        user_doc = UserRepository.create(user_data)
        user_id = user_doc.get("id")

        # 2. Create Appwrite Auth account
        auth_user = users.create(
            user_id=user_id,
            email=email,
            password=password,
            name=f"{user_info['first_name']} {user_info['last_name']}",
        )

        created_users.append({
            "db_id": user_id,
            "auth_id": auth_user.get("$id"),
            "email": email,
            "role": user_info["role"]
        })

        print(f"   ✅ Created successfully!")
        print(f"      DB ID: {user_id[:16]}...")
        print(f"      Auth ID: {auth_user.get('$id')[:16]}...")

    except AppwriteException as e:
        print(f"   ❌ Failed: {str(e)}")

# ==================== 2. RETRIEVE USERS FROM DATABASE ====================
print("\n\n📊 STEP 2: Users in Database (Collection: users)")
print("-" * 70)

try:
    url = f"{ENDPOINT}/v1/databases/{DB_ID}/collections/{USERS_COLLECTION}/documents"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        data = response.json()
        db_users = data.get("documents", [])

        print(f"\nTotal users in DB: {len(db_users)}\n")

        for user in db_users:
            user_id = user.get("$id")
            email = user.get("email")
            role = user.get("role")
            status = user.get("account_status", "N/A")
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")

            print(f"  📍 {first_name} {last_name}")
            print(f"     Email: {email}")
            print(f"     Role: {role:15} | Status: {status}")
            print(f"     ID: {user_id[:20]}...")
            print()
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error retrieving users: {str(e)}")

# ==================== 3. RETRIEVE APPWRITE AUTH ACCOUNTS ====================
print("\n📋 STEP 3: Appwrite Auth Accounts")
print("-" * 70)

try:
    url = f"{ENDPOINT}/v1/users"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        data = response.json()
        auth_users_list = data.get("users", [])

        print(f"\nTotal auth accounts: {len(auth_users_list)}\n")

        for auth_user in auth_users_list:
            auth_id = auth_user.get("$id")
            email = auth_user.get("email")
            name = auth_user.get("name", "N/A")
            status = "Active" if auth_user.get("status") else "Inactive"

            print(f"  👤 {name}")
            print(f"     Email: {email}")
            print(f"     Status: {status}")
            print(f"     ID: {auth_id[:20]}...")
            print()
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error retrieving auth accounts: {str(e)}")

# ==================== 4. SUMMARY ====================
print("\n📈 SUMMARY")
print("-" * 70)
print(f"✅ Users created in this session: {len(created_users)}")

if created_users:
    print("\n📝 Newly created users:")
    for user in created_users:
        print(f"   • {user['email']:30} ({user['role']:15})")

print("\n" + "=" * 70)
print("✨ Operation completed!")
print("=" * 70)
