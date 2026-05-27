#!/usr/bin/env python
"""Diagnostic script to check SGEP backend setup."""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def check_mark(passed):
    return f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"

def print_status(name, passed, message=""):
    status = check_mark(passed)
    print(f"  {status} {name}")
    if message:
        print(f"    └─ {message}")

# 1. Check Python version
print_header("1️⃣  PYTHON & ENVIRONMENT")
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print_status("Python version", True, f"v{py_version}")

# 2. Check .env file
print_header("2️⃣  ENVIRONMENT VARIABLES")
env_path = Path(__file__).parent / ".env"
has_env = env_path.exists()
print_status(".env file exists", has_env, str(env_path) if has_env else "Not found")

if has_env:
    from decouple import config

    # Check Appwrite config
    appwrite_endpoint = config("APPWRITE_ENDPOINT", default="")
    appwrite_project_id = config("APPWRITE_PROJECT_ID", default="")
    appwrite_api_key = config("APPWRITE_API_KEY", default="")
    appwrite_db_id = config("APPWRITE_DB_ID", default="")

    has_endpoint = bool(appwrite_endpoint)
    has_project = bool(appwrite_project_id) and appwrite_project_id != ""
    has_api_key = bool(appwrite_api_key) and appwrite_api_key != ""
    has_db_id = bool(appwrite_db_id)

    print(f"\n  {Colors.BOLD}Appwrite Configuration:{Colors.RESET}")
    print_status("APPWRITE_ENDPOINT", has_endpoint, appwrite_endpoint if has_endpoint else "Missing")
    print_status("APPWRITE_PROJECT_ID", has_project, f"{'***' + appwrite_project_id[-4:] if has_project else 'Missing'}")
    print_status("APPWRITE_API_KEY", has_api_key, f"{'***' + appwrite_api_key[-10:] if has_api_key else 'Missing'}")
    print_status("APPWRITE_DB_ID", has_db_id, appwrite_db_id if has_db_id else "Missing")

# 3. Check Python packages
print_header("3️⃣  PYTHON PACKAGES")
packages = {
    "django": "Django",
    "rest_framework": "Django REST Framework",
    "appwrite": "Appwrite SDK",
    "celery": "Celery",
    "redis": "Redis",
    "pandas": "Pandas",
    "weasyprint": "WeasyPrint",
}

for pkg, name in packages.items():
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print_status(f"{name}", True, f"v{version}")
    except ImportError:
        print_status(f"{name}", False, "Not installed")

# 4. Test Appwrite connection
print_header("4️⃣  APPWRITE CONNECTION TEST")
if has_env and has_endpoint and has_project and has_api_key:
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

        from core.services.appwrite_service import AppwriteService
        service = AppwriteService()
        print_status("Appwrite client initialization", True, "Connected")

        # Try to get database info
        try:
            databases = service.databases.list()
            print_status("Database connection", True, f"Can communicate with server")
        except Exception as e:
            error_msg = str(e)
            if "project_not_found" in error_msg or "404" in error_msg:
                print_status("Database connection", False, "Project not found (check PROJECT_ID)")
            else:
                print_status("Database connection", False, str(e)[:50])
    except Exception as e:
        print_status("Appwrite client initialization", False, str(e)[:50])
else:
    print_status("Appwrite connection test", False, "Missing Appwrite configuration")

# 5. Check external services
print_header("5️⃣  EXTERNAL SERVICES")

# Redis check
try:
    import redis
    redis_url = config("REDIS_URL", default="redis://localhost:6379/0")
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print_status("Redis", True, f"Connected to {redis_url}")
    except Exception as e:
        print_status("Redis", False, f"Cannot connect: {str(e)[:40]}")
except ImportError:
    print_status("Redis", False, "redis-py not installed")

# 6. Check Docker
print_header("6️⃣  DOCKER STATUS")
try:
    import subprocess
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.strip()
        print_status("Docker", True, version)
    else:
        print_status("Docker", False, "Command failed")
except FileNotFoundError:
    print_status("Docker", False, "Not installed")
except Exception as e:
    print_status("Docker", False, str(e)[:40])

# 7. Check docker-compose
print_header("7️⃣  DOCKER COMPOSE STATUS")
try:
    import subprocess
    result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print_status("Docker Compose", True, result.stdout.strip())
    else:
        print_status("Docker Compose", False, "Command failed")
except Exception as e:
    print_status("Docker Compose", False, str(e)[:40])

# 8. Summary & recommendations
print_header("📋 RECOMMENDATIONS")
issues = []

if not has_env:
    issues.append("• Create a .env file with Appwrite credentials")

if has_env:
    if not has_project or not has_api_key:
        issues.append("• Add APPWRITE_PROJECT_ID and APPWRITE_API_KEY to .env")

if not issues:
    issues.append("✅ All checks passed! You're ready to run setup_appwrite")

for issue in issues:
    print(issue)

print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
print("1. Ensure .env has correct Appwrite credentials")
print("2. If using Appwrite Cloud: verify Project ID exists in cloud.appwrite.io")
print("3. If using local Appwrite: run 'docker-compose up -d'")
print("4. Run: python manage.py setup_appwrite")
print()
