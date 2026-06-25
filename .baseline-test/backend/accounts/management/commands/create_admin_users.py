"""Create admin users with Appwrite authentication."""

from django.core.management.base import BaseCommand
from accounts.auth_service import AppwriteAuthService
from accounts.models import ROLE_SUPERADMIN, ROLE_COMPTABLE, ACCOUNT_STATUS_ACTIVE


class Command(BaseCommand):
    help = "Create superadmin and comptable users with Appwrite authentication"

    def add_arguments(self, parser):
        parser.add_argument(
            "--superadmin-email",
            type=str,
            default="admin@sgep.cm",
            help="Superadmin email",
        )
        parser.add_argument(
            "--superadmin-password",
            type=str,
            default="AdminPassword123!",
            help="Superadmin password",
        )
        parser.add_argument(
            "--comptable-email",
            type=str,
            default="comptable@sgep.cm",
            help="Comptable email",
        )
        parser.add_argument(
            "--comptable-password",
            type=str,
            default="ComptablePassword123!",
            help="Comptable password",
        )

    def handle(self, *args, **options):
        # Create superadmin user
        superadmin_email = options["superadmin_email"]
        superadmin_password = options["superadmin_password"]

        self.stdout.write(f"Creating superadmin user: {superadmin_email}...")
        try:
            superadmin_result = AppwriteAuthService.create_user_with_auth(
                email=superadmin_email,
                password=superadmin_password,
                user_data={
                    "first_name": "Admin",
                    "last_name": "SGEP",
                    "role": ROLE_SUPERADMIN,
                    "account_status": ACCOUNT_STATUS_ACTIVE,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Superadmin created!\n"
                    f"   Auth ID: {superadmin_result['auth_id']}\n"
                    f"   User ID: {superadmin_result['user_id']}\n"
                    f"   Email: {superadmin_result['email']}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to create superadmin: {str(e)}"))

        # Create comptable user
        comptable_email = options["comptable_email"]
        comptable_password = options["comptable_password"]

        self.stdout.write(f"\nCreating comptable user: {comptable_email}...")
        try:
            comptable_result = AppwriteAuthService.create_user_with_auth(
                email=comptable_email,
                password=comptable_password,
                user_data={
                    "first_name": "Comptable",
                    "last_name": "SGEP",
                    "role": ROLE_COMPTABLE,
                    "account_status": ACCOUNT_STATUS_ACTIVE,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Comptable created!\n"
                    f"   Auth ID: {comptable_result['auth_id']}\n"
                    f"   User ID: {comptable_result['user_id']}\n"
                    f"   Email: {comptable_result['email']}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to create comptable: {str(e)}"))

        self.stdout.write(
            self.style.SUCCESS("\n✨ Admin user setup completed!")
        )
