import { cookies } from "next/headers";
import { z } from "zod";
import { USER_ROLES, ROLE_COOKIE, type UserRole } from "@/lib/auth/constants";

const RoleSchema = z.object({
  role: z.enum([
    USER_ROLES.ADMIN,
    USER_ROLES.TEACHER,
    USER_ROLES.STUDENT,
    USER_ROLES.PARENT,
  ]),
});

const COOKIE_MAX_AGE = 30 * 60; // 30 minutes, matches Appwrite default session length

export async function POST(request: Request): Promise<Response> {
  const body: unknown = await request.json().catch(() => null);
  const parsed = RoleSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: "Invalid role." }, { status: 400 });
  }

  const isProd = process.env.NODE_ENV === "production";
  const cookieStore = await cookies();

  cookieStore.set(ROLE_COOKIE, parsed.data.role as UserRole, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: COOKIE_MAX_AGE,
    path: "/",
  });

  return new Response(null, { status: 204 });
}

export async function DELETE(): Promise<Response> {
  const cookieStore = await cookies();
  cookieStore.delete(ROLE_COOKIE);
  return new Response(null, { status: 204 });
}
