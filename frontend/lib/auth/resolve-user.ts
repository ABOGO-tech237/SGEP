import { Account, Teams, type Client } from "appwrite";

import type { SchoolUser } from "@/lib/auth";
import { TEAM_ID_TO_ROLE } from "@/lib/auth/constants";

export async function resolveSchoolUser(
  client: Client,
): Promise<SchoolUser | null> {
  const account = new Account(client);
  const teamsService = new Teams(client);
  const user = await account.get();
  const userTeams = await teamsService.list();
  const roleTeam = userTeams.teams[0];
  if (!roleTeam) return null;

  const role = TEAM_ID_TO_ROLE[roleTeam.$id];
  if (!role) return null;

  return {
    id: user.$id,
    name: user.name,
    email: user.email,
    role,
    teamId: roleTeam.$id,
  };
}
