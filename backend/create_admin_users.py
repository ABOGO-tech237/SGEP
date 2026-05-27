"""Setup admin users (basic version)."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from accounts.repository import UserRepository
from accounts.models import ROLE_SUPERADMIN, ROLE_COMPTABLE, ACCOUNT_STATUS_ACTIVE
from datetime import datetime

print("=" * 60)
print("Creating admin users")
print("=" * 60)

users_to_create = [
    {
        "email": "admin_auth@sgep.cm",
        "first_name": "Admin",
        "last_name": "SGEP",
        "role": ROLE_SUPERADMIN,
    },
    {
        "email": "comptable_auth@sgep.cm",
        "first_name": "Comptable",
        "last_name": "SGEP",
        "role": ROLE_COMPTABLE,
    }
]

for user_info in users_to_create:
    email = user_info["email"]
    print(f"\nCreating {email}...")

    try:
        now = datetime.utcnow().isoformat()
        user_data = {
            **user_info,
            "email": email.lower(),
            "account_status": ACCOUNT_STATUS_ACTIVE,
            "created_at": now,
            "updated_at": now,
        }
        user = UserRepository.create(user_data)
        print(f"✅ Created!")
        print(f"   ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('role')}")
    except Exception as e:
        print(f"❌ Failed: {str(e)}")

print("\n" + "=" * 60)
print("✨ Admin users setup completed!")
print("=" * 60)
print("\n📝 Note: Run test_auth_login.py to test authentication")
