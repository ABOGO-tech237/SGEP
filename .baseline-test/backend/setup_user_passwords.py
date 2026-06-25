"""Add missing passwords to existing Appwrite users."""

from django.contrib.auth.hashers import make_password
from accounts.repository import UserRepository
from appwrite.query import Query
from config.appwrite_client import databases
from django.conf import settings

DB_ID = settings.APPWRITE_DB_ID
USERS_COLLECTION_ID = "users"

print("=" * 60)
print("Adding passwords to users")
print("=" * 60)

# Define credentials for existing users
users_with_passwords = [
    {
        "email": "admin@sgep.cm",
        "password": "AdminPassword123!",
    },
    {
        "email": "comptable@sgep.cm",
        "password": "ComptablePassword123!",
    },
]

for user_info in users_with_passwords:
    email = user_info["email"]
    password = user_info["password"]

    print(f"\nUpdating {email}...")

    user = UserRepository.get_by_email(email)
    if not user:
        print(f"❌ User not found: {email}")
        continue

    try:
        user_id = user.get("id")
        hashed_password = make_password(password)

        updated_user = UserRepository.update(user_id, {"password": hashed_password})
        print(f"✅ Password updated for {email}")
        print(f"   User ID: {user_id}")
    except Exception as e:
        print(f"❌ Failed to update {email}: {str(e)}")

print("\n" + "=" * 60)
print("✨ Password setup completed!")
print("=" * 60)
