"""Link existing users to Appwrite Auth with default passwords."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from config.appwrite_client import users
from appwrite.exception import AppwriteException

print("=" * 60)
print("Creating Appwrite Auth accounts for users")
print("=" * 60)

users_to_link = [
    {
        "user_id": "6a11d268985d90d20c82",
        "email": "admin_auth@sgep.cm",
        "password": "AdminPassword123!",
        "name": "Admin SGEP"
    },
    {
        "user_id": "6a11d26fa28eb446e8a8",
        "email": "comptable_auth@sgep.cm",
        "password": "ComptablePassword123!",
        "name": "Comptable SGEP"
    }
]

for user_info in users_to_link:
    user_id = user_info["user_id"]
    email = user_info["email"]
    password = user_info["password"]
    name = user_info["name"]

    print(f"\nLinking {email} to Appwrite Auth...")

    try:
        # Create Appwrite Auth account with the same user_id
        auth_user = users.create(
            user_id=user_id,
            email=email,
            password=password,
            name=name,
        )
        print(f"✅ Appwrite Auth account created!")
        print(f"   Email: {auth_user.get('email')}")
        print(f"   ID: {auth_user.get('$id')}")
        print(f"   Status: {auth_user.get('status')}")
    except AppwriteException as e:
        print(f"❌ Failed: {str(e)}")

print("\n" + "=" * 60)
print("✨ Appwrite Auth linking completed!")
print("=" * 60)
