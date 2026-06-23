"""Create or reset a single Appwrite user with a hashed password for Django login."""

from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from accounts.auth_service import AppwriteAuthService
from accounts.models import (
    ACCOUNT_STATUS_ACTIVE,
    ROLE_COMPTABLE,
    ROLE_PARENT,
    ROLE_SUPERADMIN,
)
from accounts.repository import UserRepository


class Command(BaseCommand):
    help = (
        "Crée un utilisateur Appwrite (auth + document users) avec mot de passe hashé "
        "pour la connexion via auth/login/.\n\n"
        "Exemple (Render shell) :\n"
        "  python manage.py create_login_user\n"
        "  python manage.py create_login_user --email admin@sgep.cm --password AdminPassword123!\n\n"
        "Identifiants par défaut : admin@sgep.cm / AdminPassword123! (superadmin)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="admin@sgep.cm",
            help="Email de connexion (défaut: admin@sgep.cm)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="AdminPassword123!",
            help="Mot de passe en clair, hashé avant stockage (défaut: AdminPassword123!)",
        )
        parser.add_argument(
            "--role",
            type=str,
            default=ROLE_SUPERADMIN,
            choices=[ROLE_SUPERADMIN, ROLE_COMPTABLE, ROLE_PARENT],
            help="Rôle utilisateur (défaut: superadmin)",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            default="Admin",
            help="Prénom (défaut: Admin)",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            default="SGEP",
            help="Nom (défaut: SGEP)",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        role = options["role"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        existing = UserRepository.get_by_email(email=email)
        if existing:
            self.stdout.write(f"Utilisateur existant ({email}), mise à jour du mot de passe...")
            user_id = existing.get("id")
            now_iso = datetime.utcnow().isoformat()
            UserRepository.update(
                user_id=user_id,
                data={
                    "password": make_password(password),
                    "updated_at": now_iso,
                },
            )
            auth_id = user_id
            try:
                AppwriteAuthService.update_user_password(user_id=user_id, password=password)
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(
                        f"Document users mis à jour, mais auth Appwrite non mis à jour : {exc}"
                    )
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Mot de passe mis à jour pour {email}\n"
                    f"   User ID: {user_id}\n"
                    f"   Auth ID: {auth_id}\n"
                    f"   Role: {existing.get('role', role)}"
                )
            )
            return

        self.stdout.write(f"Création de l'utilisateur {email} (role={role})...")
        result = AppwriteAuthService.create_user_with_auth(
            email=email,
            password=password,
            user_data={
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "account_status": ACCOUNT_STATUS_ACTIVE,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Utilisateur créé avec succès !\n"
                f"   Email: {result['email']}\n"
                f"   Auth ID: {result['auth_id']}\n"
                f"   User ID: {result['user_id']}\n"
                f"   Role: {result['role']}\n"
                f"   Connexion : POST /api/v1/auth/login/ avec email et mot de passe."
            )
        )
