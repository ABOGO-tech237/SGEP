import { ID } from "appwrite";
import { createAppwriteClient, createAccount, createTeams } from "./appwrite";
import { resolveSchoolUser } from "./auth/resolve-user";
import { type UserRole, TEAM_IDS } from "./auth/constants";

export interface SchoolUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  teamId: string;
}

export async function login(
  email: string,
  password: string,
): Promise<SchoolUser> {
  const client = createAppwriteClient();
  const account = createAccount(client);
  console.log("[auth] attempting createEmailPasswordSession...");
  try {
    const session = await account.createEmailPasswordSession(email, password);
    console.log("[auth] session created:", session.$id);
  } catch (err: unknown) {
    const e = err as { code?: number; type?: string; message?: string };
    console.error("[auth] createEmailPasswordSession failed:", {
      code: e?.code,
      type: e?.type,
      message: e?.message,
    });
    throw err;
  }
  const user = await getAuthUser();
  if (!user) throw new Error("Login failed — session created but no team membership found");
  return user;
}

export async function logout(): Promise<void> {
  const account = createAccount();
  await account.deleteSession("current");
}

export async function getAuthUser(): Promise<SchoolUser | null> {
  try {
    const client = createAppwriteClient();
    console.log("[auth] getAuthUser: resolving user from Appwrite session...");
    return await resolveSchoolUser(client);
  } catch (err: unknown) {
    const e = err as { code?: number; type?: string; message?: string };
    console.warn("[auth] getAuthUser failed:", {
      code: e?.code,
      type: e?.type,
      message: e?.message,
    });
    return null;
  }
}

export async function registerUser(
  name: string,
  email: string,
  password: string,
  role: UserRole,
) {
  const client = createAppwriteClient();
  const account = createAccount(client);
  const teamsService = createTeams(client);
  const user = await account.create(ID.unique(), email, password, name);
  await teamsService.createMembership(
    TEAM_IDS[role],
    ["member"],
    email,
    user.$id,
    undefined,
    `${process.env.NEXT_PUBLIC_APP_URL}/auth/verify`,
  );
  return user;
}

export async function sendPasswordReset(email: string) {
  const account = createAccount();
  return account.createRecovery(
    email,
    `${process.env.NEXT_PUBLIC_APP_URL}/reset-password`,
  );
}

export async function confirmPasswordReset(
  userId: string,
  secret: string,
  newPassword: string,
) {
  const account = createAccount();
  return account.updateRecovery(userId, secret, newPassword);
}
