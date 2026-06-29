#!/bin/bash
# Run Appwrite Cloud integration tests for user management

set -e

echo "=========================================="
echo "🚀 SGEP User Integration Tests"
echo "=========================================="
echo ""

# Check if APPWRITE credentials are set
if [ -z "$APPWRITE_PROJECT_ID" ]; then
    echo "⚠️  APPWRITE_PROJECT_ID not set in environment"
    echo "Loading from .env file..."
    set -a
    source .env
    set +a
fi

if [ -z "$APPWRITE_API_KEY" ]; then
    echo "❌ APPWRITE_API_KEY is not configured"
    exit 1
fi

echo "✅ Appwrite credentials loaded"
echo ""

# Run the Appwrite integration tests
echo "🧪 Running user creation tests with Appwrite Cloud..."
python manage.py test accounts.tests_appwrite -v 2

echo ""
echo "✅ All user integration tests completed!"
echo ""
echo "Test Results Summary:"
echo "  - Superadmin user creation"
echo "  - Comptable user creation"
echo "  - Parent user creation"
echo "  - User retrieval by email"
echo "  - User retrieval by ID"
echo "  - User status updates"
echo "  - Multiple user creation"
echo "  - Case-insensitive email lookup"
echo ""
