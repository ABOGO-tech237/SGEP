import { getSessionUser } from "@/lib/server/resolve-session-user";

export async function GET(): Promise<Response> {
  const user = await getSessionUser();
  if (!user) {
    return Response.json({ error: "Unauthorized." }, { status: 401 });
  }

  return Response.json({ user });
}
