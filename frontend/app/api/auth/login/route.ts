import { cookies } from "next/headers";
import { decodeJwt } from "jose";
import { TEAM_IDS, USER_ROLES } from "@/lib/auth/constants";
import { LoginSchema } from "@/lib/types/auth";
import type { LoginApiResponse, LoginApiRole } from "@/lib/types/auth";

const SESSION_COOKIE = "psms_session";
const CSRF_COOKIE = "psms_csrf";
const SESSION_MAX_AGE = 30 * 60; // 30 minutes

function normalizeRole(role: string): LoginApiRole {
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

  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl) {
    return Response.json({ error: "Service unavailable." }, { status: 503 });
  }

  let djangoRes: Response;
  try {
    djangoRes = await fetch(`${apiUrl}/api/v1/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(parsed.data),
    });
  } catch {
    return Response.json({ error: "Service unavailable." }, { status: 503 });
  }

  if (!djangoRes.ok) {
    return Response.json(
      { error: "Invalid email or password." },
      { status: 401 },
    );
  }

  const djangoData = (await djangoRes.json()) as {
    access_token?: string;
    refresh_token?: string;
    access?: string;
    refresh?: string;
  };

  const accessToken = djangoData.access_token ?? djangoData.access;
  const refreshToken = djangoData.refresh_token ?? djangoData.refresh;
  if (!accessToken || !refreshToken) {
    return Response.json(
      { error: "Service unavailable." },
      { status: 502 },
    );
  }

  const jwtPayload = decodeJwt(accessToken) as {
    role?: string;
    email?: string;
    account_status?: string;
    student_id?: string | null;
    user_id?: string;
    sub?: string;
  };

  const role = normalizeRole(jwtPayload.role ?? USER_ROLES.ADMIN);
  const email = jwtPayload.email ?? "";
  const userId = jwtPayload.user_id ?? jwtPayload.sub ?? "";
  const name = email || userId || "User";

  const cookieStore = await cookies();
  const isProd = process.env.NODE_ENV === "production";

  cookieStore.set(SESSION_COOKIE, accessToken, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: SESSION_MAX_AGE,
    path: "/",
  });

  cookieStore.set(CSRF_COOKIE, crypto.randomUUID(), {
    httpOnly: false,
    secure: isProd,
    sameSite: "strict",
    maxAge: SESSION_MAX_AGE,
    path: "/",
  });

  const responseBody: LoginApiResponse = {
    role,
    user: {
      id: userId,
      email,
      name,
      role,
      teamId: TEAM_IDS[role],
    },
  };

  return Response.json(responseBody);
}
