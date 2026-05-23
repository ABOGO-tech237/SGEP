import { ID } from "appwrite";
import { createAppwriteClient, createAccount, createTeams } from "./appwrite";
import { type UserRole } from "./auth/constants";

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
  await account.createEmailPasswordSession(email, password);
  const user = await getAuthUser();
  if (!user) throw new Error("Login failed");
  return user;
}

export async function logout(): Promise<void> {
  const account = createAccount();
  await account.deleteSession("current");
}

export async function getAuthUser(): Promise<SchoolUser | null> {
  try {
    const client = createAppwriteClient();
    const account = createAccount(client);
    const teamsService = createTeams(client);
    const user = await account.get();
    const userTeams = await teamsService.list();
    const roleTeam = userTeams.teams[0];
    if (!roleTeam) return null;
    return {
      id: user.$id,
      name: user.name,
      email: user.email,
      role: roleTeam.name.toLowerCase() as UserRole,
      teamId: roleTeam.$id,
    };
  } catch {
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
    role + "s",
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
