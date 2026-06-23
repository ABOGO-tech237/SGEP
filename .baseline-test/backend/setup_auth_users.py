"""Setup admin users with proper authentication."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from accounts.auth_service import AppwriteAuthService
from accounts.models import ROLE_SUPERADMIN, ROLE_COMPTABLE, ACCOUNT_STATUS_ACTIVE
from datetime import datetime
from django.contrib.auth.hashers import make_password
from accounts.repository import UserRepository

print("=" * 60)
print("Creating admin users with authentication")
print("=" * 60)

# Admin user
admin_email = "admin_auth@sgep.cm"
admin_password = "AdminPassword123!"

print(f"\n1. Creating superadmin: {admin_email}")
try:
    now = datetime.utcnow().isoformat()
    admin_data = {
        "email": admin_email.lower(),
        "first_name": "Admin",
        "last_name": "SGEP",
        "role": ROLE_SUPERADMIN,
        "account_status": ACCOUNT_STATUS_ACTIVE,
        "password": make_password(admin_password),
        "created_at": now,
        "updated_at": now,
    }
    admin_user = UserRepository.create(admin_data)
    print(f"✅ Admin created!")
    print(f"   ID: {admin_user.get('id')}")
    print(f"   Email: {admin_user.get('email')}")
    print(f"   Role: {admin_user.get('role')}")
except Exception as e:
    print(f"❌ Failed: {str(e)}")

# Comptable user
comptable_email = "comptable_auth@sgep.cm"
comptable_password = "ComptablePassword123!"

print(f"\n2. Creating comptable: {comptable_email}")
try:
    now = datetime.utcnow().isoformat()
    comptable_data = {
        "email": comptable_email.lower(),
        "first_name": "Comptable",
        "last_name": "SGEP",
        "role": ROLE_COMPTABLE,
        "account_status": ACCOUNT_STATUS_ACTIVE,
        "password": make_password(comptable_password),
        "created_at": now,
        "updated_at": now,
    }
    comptable_user = UserRepository.create(comptable_data)
    print(f"✅ Comptable created!")
    print(f"   ID: {comptable_user.get('id')}")
    print(f"   Email: {comptable_user.get('email')}")
    print(f"   Role: {comptable_user.get('role')}")
except Exception as e:
    print(f"❌ Failed: {str(e)}")

print("\n" + "=" * 60)
print("✨ Admin users setup completed!")
print("=" * 60)
