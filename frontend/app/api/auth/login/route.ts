import { cookies } from "next/headers";
import { decodeJwt } from "jose";

import {
  DJANGO_ACCESS_COOKIE,
  DJANGO_REFRESH_COOKIE,
  TEAM_IDS,
  USER_ROLES,
} from "@/lib/auth/constants";
import {
  DjangoAuthError,
  loginWithDjango,
} from "@/lib/server/django-auth";
import { LoginSchema } from "@/lib/types/auth";
import type { LoginApiResponse, LoginApiRole } from "@/lib/types/auth";

const CSRF_COOKIE = "psms_csrf";
const DEFAULT_SESSION_MAX_AGE = 30 * 60;
const DJANGO_REFRESH_MAX_AGE = 7 * 24 * 60 * 60;

function normalizeRole(role: string | undefined): LoginApiRole {
  if (role === "superadmin" || role === "comptable") {
    return USER_ROLES.ADMIN;
  }

  if (
    role === USER_ROLES.ADMIN ||
    role === USER_ROLES.TEACHER ||
    role === USER_ROLES.STUDENT ||
    role === USER_ROLES.PARENT
  ) {
    return role;
  }

  return USER_ROLES.ADMIN;
}

export async function POST(request: Request): Promise<Response> {
  const body: unknown = await request.json().catch(() => null);

  const parsed = LoginSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }

  let djangoTokens;
  try {
    djangoTokens = await loginWithDjango(
      parsed.data.email,
      parsed.data.password,
    );
  } catch (error) {
    if (error instanceof DjangoAuthError) {
      if (error.code === "NOT_CONFIGURED") {
        return Response.json({ error: "Service unavailable." }, { status: 503 });
      }
      return Response.json(
        { error: "Invalid email or password." },
        { status: 401 },
      );
    }
    return Response.json({ error: "Service unavailable." }, { status: 503 });
  }

  const claims = decodeJwt(djangoTokens.accessToken) as {
    role?: string;
    email?: string;
    user_id?: string;
    sub?: string;
  };

  const role = normalizeRole(claims.role);
  const email = claims.email ?? parsed.data.email;
  const userId = claims.user_id ?? claims.sub ?? "";
  const name = email || userId || "User";

  const cookieStore = await cookies();
  const isProd = process.env.NODE_ENV === "production";

  cookieStore.set(DJANGO_ACCESS_COOKIE, djangoTokens.accessToken, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: DEFAULT_SESSION_MAX_AGE,
    path: "/",
  });

  cookieStore.set(DJANGO_REFRESH_COOKIE, djangoTokens.refreshToken, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: DJANGO_REFRESH_MAX_AGE,
    path: "/",
  });

  cookieStore.set(CSRF_COOKIE, crypto.randomUUID(), {
    httpOnly: false,
    secure: isProd,
    sameSite: "strict",
    maxAge: DEFAULT_SESSION_MAX_AGE,
    path: "/",
  });

  const responseBody: LoginApiResponse = {
    role,
    user: {
      id: userId,
      name,
      email,
      role,
      teamId: TEAM_IDS[role],
    },
  };

  return Response.json(responseBody);
}
