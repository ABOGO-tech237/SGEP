import { cookies } from "next/headers";

const SESSION_COOKIE = "psms_session";
const CSRF_COOKIE = "psms_csrf";

export async function POST(request: Request): Promise<Response> {
  const cookieStore = await cookies();

  const csrfHeader = request.headers.get("X-CSRF-Token");
  const csrfCookie = cookieStore.get(CSRF_COOKIE)?.value;

  if (!csrfHeader || !csrfCookie || csrfHeader !== csrfCookie) {
    return Response.json({ error: "Forbidden." }, { status: 403 });
  }

  cookieStore.delete(SESSION_COOKIE);
  cookieStore.delete(CSRF_COOKIE);

  return new Response(null, { status: 204 });
}
