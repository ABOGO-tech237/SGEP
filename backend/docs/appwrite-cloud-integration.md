# Appwrite Cloud Integration

This backend is configured to use Appwrite Cloud instead of a local Docker Appwrite instance.

## Environment variables

Set these values in your `.env` file:

- `APPWRITE_ENDPOINT=https://<your-region>.cloud.appwrite.io/v1`
- `APPWRITE_PROJECT_ID=<your-project-id>`
- `APPWRITE_API_KEY=<server-api-key>`
- `APPWRITE_DB_ID=sgep_db`
- `MEDICAL_ENCRYPTION_KEY=<fernet-key>`

The `MEDICAL_ENCRYPTION_KEY` is used to encrypt and decrypt the `medical` payload stored on student documents.

## Configuration points

- `config/settings.py` reads all Appwrite and encryption values from environment variables.
- `config/appwrite_client.py` builds the shared Appwrite SDK client against Appwrite Cloud.
- `core/services/appwrite_service.py` uses the same cloud client and server API key.
- `core/management/commands/setup_appwrite.py` should be run against the cloud project to create or update collections.

## Operational notes

- Use a server-side Appwrite API key with database write permissions.
- Keep the endpoint region aligned with the Appwrite project region.
- The setup command is idempotent and can be re-run after schema updates.

## Quick verification

1. Populate `.env` with the cloud values.
2. Run `python manage.py check`.
3. Run the Appwrite setup command against the cloud project.
4. Run `python manage.py verify_appwrite` to confirm connectivity.
5. Run integration tests: `python manage.py test core.tests_appwrite_integration -v 2`.

See [appwrite-integration-tests.md](appwrite-integration-tests.md) for the full testing guide.