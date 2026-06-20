import { decodeJwt } from "jose";
import { cookies } from "next/headers";

import type { SchoolUser } from "@/lib/auth";
import {
  DJANGO_ACCESS_COOKIE,
  DJANGO_REFRESH_COOKIE,
  TEAM_IDS,
  USER_ROLES,
} from "@/lib/auth/constants";
import type { UserRole } from "@/lib/auth/constants";
import { refreshDjangoAccessToken } from "@/lib/server/django-auth";

function normalizeRole(role: string | undefined): UserRole {
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

function userFromAccessToken(accessToken: string): SchoolUser | null {
  let claims: {
    role?: string;
    email?: string;
    user_id?: string;
    sub?: string;
  };
  try {
    claims = decodeJwt(accessToken);
  } catch {
    return null;
  }

  const role = normalizeRole(claims.role);
  const email = claims.email ?? "";
  const id = claims.user_id ?? claims.sub ?? "";
  const name = email || id || "User";

  return {
    id,
    name,
    email,
    role,
    teamId: TEAM_IDS[role],
  };
}

export async function getSessionUser(): Promise<SchoolUser | null> {
  const cookieStore = await cookies();

  const accessToken = cookieStore.get(DJANGO_ACCESS_COOKIE)?.value;
  if (accessToken) {
    const user = userFromAccessToken(accessToken);
    if (user) return user;
  }

  const refreshToken = cookieStore.get(DJANGO_REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return null;
  }

  const refreshed = await refreshDjangoAccessToken(refreshToken);
  if (!refreshed) {
    return null;
  }

  cookieStore.set(DJANGO_ACCESS_COOKIE, refreshed, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: 30 * 60,
    path: "/",
  });

  return userFromAccessToken(refreshed);
}
