import { cookies } from "next/headers";
import { LoginSchema } from "@/lib/types/auth";
import type { LoginApiResponse } from "@/lib/types/auth";

const SESSION_COOKIE = "psms_session";
const CSRF_COOKIE = "psms_csrf";
const SESSION_MAX_AGE = 30 * 60; // 30 minutes

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
    djangoRes = await fetch(`${apiUrl}/auth/login/`, {
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
    access: string;
    role: string;
    user: { id: string; email: string; name: string };
  };

  const cookieStore = await cookies();
  const isProd = process.env.NODE_ENV === "production";

  cookieStore.set(SESSION_COOKIE, djangoData.access, {
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
    role: djangoData.role as LoginApiResponse["role"],
    user: {
      id: djangoData.user.id,
      email: djangoData.user.email,
      name: djangoData.user.name,
      role: djangoData.role as LoginApiResponse["role"],
    },
  };

  return Response.json(responseBody);
}
