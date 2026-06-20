import { Account, Client } from "appwrite";
import type { Models } from "appwrite";

import type { SchoolUser } from "@/lib/auth";
import { resolveSchoolUser } from "@/lib/auth/resolve-user";
import { assertAppwriteConfig } from "@/lib/server/appwrite-config";

export class AppwriteAuthError extends Error {
  constructor(
    message: string,
    public readonly code:
      | "NOT_CONFIGURED"
      | "INVALID_CREDENTIALS"
      | "NO_TEAM"
      | "UNKNOWN",
  ) {
    super(message);
    this.name = "AppwriteAuthError";
  }
}

function createAdminClient(): Client {
  const { endpoint, projectId, apiKey } = assertAppwriteConfig();
  if (!apiKey) {
    throw new AppwriteAuthError("Appwrite API key missing", "NOT_CONFIGURED");
  }

  return new Client()
    .setEndpoint(endpoint)
    .setProject(projectId)
    .setKey(apiKey);
}

export function createSessionClient(sessionSecret: string): Client {
  const { endpoint, projectId } = assertAppwriteConfig();
  return new Client()
    .setEndpoint(endpoint)
    .setProject(projectId)
    .setSession(sessionSecret);
}

export async function loginWithAppwrite(
  email: string,
  password: string,
): Promise<{
  user: SchoolUser;
  sessionSecret: string;
  sessionExpire: Date | null;
}> {
  let session: Models.Session;
  try {
    const account = new Account(createAdminClient());
    session = await account.createEmailPasswordSession(email, password);
  } catch {
    throw new AppwriteAuthError("Invalid credentials", "INVALID_CREDENTIALS");
  }

  if (!session.secret) {
    throw new AppwriteAuthError(
      "Session secret missing — ensure APPWRITE_API_KEY has sessions.write scope",
      "NOT_CONFIGURED",
    );
  }

  const user = await resolveSchoolUser(createSessionClient(session.secret));
  if (!user) {
    throw new AppwriteAuthError("No team membership", "NO_TEAM");
  }

  return {
    user,
    sessionSecret: session.secret,
    sessionExpire: session.expire ? new Date(session.expire) : null,
  };
}

export async function logoutAppwriteSession(sessionSecret: string): Promise<void> {
  try {
    const account = new Account(createSessionClient(sessionSecret));
    await account.deleteSession("current");
  } catch {
    // Cookie is cleared even if Appwrite session deletion fails.
  }
}
