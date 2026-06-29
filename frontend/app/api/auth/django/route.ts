import { cookies } from "next/headers";
import { z } from "zod";
import { DJANGO_ACCESS_COOKIE } from "@/lib/auth/constants";

const BodySchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

const COOKIE_MAX_AGE = 43200; // 12 hours
const UPSTREAM_TIMEOUT_MS = 30_000;

export async function POST(request: Request): Promise<Response> {
  const body: unknown = await request.json().catch(() => null);
  const parsed = BodySchema.safeParse(body);
  if (!parsed.success) {
    return Response.json({ error: "Invalid payload." }, { status: 400 });
  }

  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl) {
    return Response.json({ error: "Server misconfigured." }, { status: 500 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${apiUrl}/api/v1/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: parsed.data.email,
        password: parsed.data.password,
      }),
      cache: "no-store",
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
    });
  } catch {
    return Response.json(
      { error: "Could not reach the backend. Please try again in a moment." },
      { status: 503 },
    );
  }

  if (!upstream.ok) {
    const detail = await upstream.json().catch(() => ({}));
    return Response.json(
      { error: (detail as { detail?: string }).detail ?? "Login failed." },
      { status: upstream.status },
    );
  }

  const { access_token } = (await upstream.json()) as { access_token: string };
  const cookieStore = await cookies();
  const isProd = process.env.NODE_ENV === "production";

  cookieStore.set(DJANGO_ACCESS_COOKIE, access_token, {
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
  cookieStore.set(DJANGO_ACCESS_COOKIE, "", { maxAge: 0, path: "/" });
  return new Response(null, { status: 204 });
}
