#!/bin/bash
# Configuration checker

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🔍 APPWRITE CONFIGURATION CHECKER                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

echo "📝 .env file contents (masked for security):"
echo "─────────────────────────────────────────────────────────────"
grep -E "^APPWRITE" backend/.env 2>/dev/null | sed 's/=.*/=***/' || echo "No .env file"
echo

echo "✅ What you NEED to do:"
echo "─────────────────────────────────────────────────────────────"
echo
echo "Option 1: Use Appwrite Cloud (https://cloud.appwrite.io)"
echo "  1. Go to https://cloud.appwrite.io and sign up"
echo "  2. Create a new project"
echo "  3. Go to Settings → API Keys"
echo "  4. Create an API key with permission to create databases"
echo "  5. Copy these values to backend/.env:"
echo
echo "     APPWRITE_ENDPOINT=https://[your-region].cloud.appwrite.io/v1"
echo "     APPWRITE_PROJECT_ID=[project_id from Settings]"
echo "     APPWRITE_API_KEY=[api_key you created]"
echo "     APPWRITE_DB_ID=sgep_db  # or any ID you want"
echo
echo "─────────────────────────────────────────────────────────────"
echo
echo "Option 2: Use Local Appwrite (Docker)"
echo "  1. Make sure Docker is running"
echo "  2. Run: docker compose up -d"
echo "  3. Wait for containers to start (~30 seconds)"
echo "  4. Update backend/.env with:"
echo
echo "     APPWRITE_ENDPOINT=http://localhost:8080/v1"
echo "     APPWRITE_PROJECT_ID=[get from http://localhost:8080]"
echo "     APPWRITE_API_KEY=[get from Appwrite dashboard]"
echo "     APPWRITE_DB_ID=sgep_db"
echo
echo "─────────────────────────────────────────────────────────────"
echo
echo "❓ Which option would you like to use?"
echo "   Enter 'cloud' for Appwrite Cloud"
echo "   Enter 'local' for Docker Appwrite"
echo "   Enter 'skip' to skip setup"
echo
