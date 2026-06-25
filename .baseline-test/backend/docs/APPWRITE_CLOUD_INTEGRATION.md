# Intégration Appwrite Cloud (Online)

Ce document explique comment configurer et utiliser Appwrite Cloud pour le projet SGEP.

## 1. Création d'un compte et d'un projet
1. Rendez-vous sur [appwrite.io](https://appwrite.io/) et connectez-vous ou créez un compte.
2. Créez un nouveau projet nommé **SGEP**.
3. Notez le **Project ID** qui s'affiche dans les paramètres du projet.

## 2. Configuration d'une clé d'API
1. Dans votre console Appwrite, allez dans **Overview** > **API Keys**.
2. Cliquez sur **Create API Key**.
3. Nommez-la `SGEP_BACKEND_KEY`.
4. Sélectionnez les scopes suivants (minimum requis) :
   - `databases.read`
   - `databases.write`
   - `collections.read`
   - `collections.write`
   - `attributes.read`
   - `attributes.write`
   - `indexes.read`
   - `indexes.write`
   - `documents.read`
   - `documents.write`
   - `users.read`
   - `users.write`
   - `messaging.read`
   - `messaging.write`
5. Copiez la clé générée.

## 3. Mise à jour des variables d'environnement
Dans votre fichier `backend/.env`, mettez à jour les variables suivantes :

```env
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=votre_project_id
APPWRITE_API_KEY=votre_api_key
APPWRITE_DB_ID=sgep_db
```

## 4. Initialisation de la base de données
Une fois les variables configurées, lancez la commande d'initialisation :

```bash
python manage.py setup_appwrite
```

Cette commande créera automatiquement la base de données `sgep_db` ainsi que toutes les collections, attributs et index nécessaires sur Appwrite Cloud.

## 5. Notes importantes
- L'utilisation de Appwrite Cloud élimine le besoin de faire tourner Appwrite localement via Docker pour la persistence des données.
- Assurez-vous que votre adresse IP est autorisée si vous avez configuré des restrictions CORS ou d'IP sur Appwrite Cloud.
