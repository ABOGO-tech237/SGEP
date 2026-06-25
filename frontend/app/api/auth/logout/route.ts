import { cookies } from "next/headers";

import {
  DJANGO_ACCESS_COOKIE,
  DJANGO_REFRESH_COOKIE,
  SESSION_COOKIE,
} from "@/lib/auth/constants";
import { logoutDjango } from "@/lib/server/django-auth";

const CSRF_COOKIE = "psms_csrf";

export async function POST(request: Request): Promise<Response> {
  const cookieStore = await cookies();

  const csrfHeader = request.headers.get("X-CSRF-Token");
  const csrfCookie = cookieStore.get(CSRF_COOKIE)?.value;

  if (!csrfHeader || !csrfCookie || csrfHeader !== csrfCookie) {
    return Response.json({ error: "Forbidden." }, { status: 403 });
  }

  const refreshToken = cookieStore.get(DJANGO_REFRESH_COOKIE)?.value;
  const accessToken = cookieStore.get(DJANGO_ACCESS_COOKIE)?.value;
  if (refreshToken) {
    await logoutDjango(refreshToken, accessToken);
  }

  cookieStore.delete(SESSION_COOKIE);
  cookieStore.delete(DJANGO_ACCESS_COOKIE);
  cookieStore.delete(DJANGO_REFRESH_COOKIE);
  cookieStore.delete(CSRF_COOKIE);

  return new Response(null, { status: 204 });
}
