import { cookies } from "next/headers";
import { z } from "zod";
import { DJANGO_TOKEN_COOKIE } from "@/lib/auth/constants";

const BodySchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

const JWT_MAX_AGE = 900; // 15 min — matches Django JWT_ACCESS_TOKEN_LIFETIME

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

  const upstream = await fetch(`${apiUrl}/api/v1/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: parsed.data.email,
      password: parsed.data.password,
    }),
    cache: "no-store",
  });

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

  cookieStore.set(DJANGO_TOKEN_COOKIE, access_token, {
    httpOnly: true,
    secure: isProd,
    sameSite: "strict",
    maxAge: JWT_MAX_AGE,
    path: "/",
  });

  return new Response(null, { status: 204 });
}

export async function DELETE(): Promise<Response> {
  const cookieStore = await cookies();
  cookieStore.delete(DJANGO_TOKEN_COOKIE);
  return new Response(null, { status: 204 });
}
