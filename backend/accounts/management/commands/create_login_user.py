"""Create or reset a single Appwrite user with a hashed password for Django login."""

from django.core.management.base import BaseCommand

from accounts.login_user_service import create_or_reset_login_user
from accounts.models import ROLE_COMPTABLE, ROLE_PARENT, ROLE_SUPERADMIN


class Command(BaseCommand):
    help = (
        "Crée un utilisateur Appwrite (auth + document users) avec mot de passe hashé "
        "pour la connexion via auth/login/.\n\n"
        "Exemple (shell local ou Render) :\n"
        "  python manage.py create_login_user\n"
        "  python manage.py create_login_user --email admin@sgep.cm --password AdminPassword123!\n\n"
        "Sans accès shell (ex. Render) : définir BOOTSTRAP_SECRET sur le serveur, "
        "puis POST /api/v1/auth/bootstrap/ avec l'en-tête X-Bootstrap-Token "
        "(voir backend/README.md).\n\n"
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
        email = options["email"]
        password = options["password"]
        role = options["role"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        existing_msg = f"Utilisateur existant ({email.strip().lower()}), mise à jour du mot de passe..."
        create_msg = f"Création de l'utilisateur {email.strip().lower()} (role={role})..."

        from accounts.repository import UserRepository

        if UserRepository.get_by_email(email=email.strip().lower()):
            self.stdout.write(existing_msg)
        else:
            self.stdout.write(create_msg)

        result = create_or_reset_login_user(
            email=email,
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name,
        )

        if result["action"] == "updated":
            if not result.get("auth_updated"):
                self.stdout.write(
                    self.style.WARNING(
                        "Document users mis à jour, mais auth Appwrite non mis à jour : "
                        f"{result.get('auth_error')}"
                    )
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Mot de passe mis à jour pour {result['email']}\n"
                    f"   User ID: {result['user_id']}\n"
                    f"   Auth ID: {result['auth_id']}\n"
                    f"   Role: {result['role']}"
                )
            )
            return

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
