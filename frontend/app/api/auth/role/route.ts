import { cookies } from "next/headers";
import { SignJWT } from "jose";
import { z } from "zod";
import {
  USER_ROLES,
  ROLE_COOKIE,
  PROXY_SESSION_COOKIE,
  type UserRole,
} from "@/lib/auth/constants";

const RoleSchema = z.object({
  role: z.enum([
    USER_ROLES.ADMIN,
    USER_ROLES.TEACHER,
    USER_ROLES.STUDENT,
    USER_ROLES.PARENT,
  ]),
});

const COOKIE_MAX_AGE = 12 * 60 * 60; // 12 hours

export async function POST(request: Request): Promise<Response> {
  const body: unknown = await request.json().catch(() => null);
  const parsed = RoleSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: "Invalid role." }, { status: 400 });
  }

  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    return Response.json({ error: "Server misconfigured." }, { status: 500 });
  }

  const isProd = process.env.NODE_ENV === "production";
  const cookieOpts = {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict" as const,
    maxAge: COOKIE_MAX_AGE,
    path: "/",
  };

  const cookieStore = await cookies();

  cookieStore.set(ROLE_COOKIE, parsed.data.role as UserRole, cookieOpts);

  // Proxy JWT — verified by Edge middleware to enforce RBAC without calling Appwrite per request
  const proxyJwt = await new SignJWT({
    role: parsed.data.role.toUpperCase(),
    sub: parsed.data.role,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime("12h")
    .sign(new TextEncoder().encode(jwtSecret));

  cookieStore.set(PROXY_SESSION_COOKIE, proxyJwt, cookieOpts);

  return new Response(null, { status: 204 });
}

export async function DELETE(): Promise<Response> {
  const cookieStore = await cookies();
  const clearOpts = { maxAge: 0, path: "/" };
  cookieStore.set(ROLE_COOKIE, "", clearOpts);
  cookieStore.set(PROXY_SESSION_COOKIE, "", clearOpts);
  return new Response(null, { status: 204 });
}
