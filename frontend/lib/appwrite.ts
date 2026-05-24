import { Client, Account, Databases, Storage, Teams } from "appwrite";

export function createAppwriteClient(): Client {
  const endpoint = process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT;
  const projectId = process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID;
  console.log("[appwrite] client init", { endpoint, projectId });
  return new Client()
    .setEndpoint(endpoint!)
    .setProject(projectId!);
}

export function createAccount(client?: Client): Account {
  return new Account(client ?? createAppwriteClient());
}

export function createDatabases(client?: Client): Databases {
  return new Databases(client ?? createAppwriteClient());
}

export function createStorage(client?: Client): Storage {
  return new Storage(client ?? createAppwriteClient());
}

export function createTeams(client?: Client): Teams {
  return new Teams(client ?? createAppwriteClient());
}
