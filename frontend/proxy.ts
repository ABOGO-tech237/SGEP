import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";
import { SESSION_COOKIE } from "@/lib/auth/constants";

const LOGIN_URL = "/login";

// Maps JWT role claim values to the route prefix they're allowed to access.
// Role names match Django's conventions (SCREAMING_SNAKE_CASE).
const JWT_ROLE_ROUTES: Record<string, string> = {
  SUPER_ADMIN: "/admin",
  ADMIN: "/admin",
  TEACHER: "/teacher",
  STUDENT: "/student",
  PARENT: "/parent",
  ACCOUNTANT: "/accountant",
};

const PROTECTED_PREFIXES = [...new Set(Object.values(JWT_ROLE_ROUTES))];

function isProtectedRoute(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

function buildCsp(nonce: string): string {
  const isDev = process.env.NODE_ENV === "development";
  const appwriteOrigin = new URL(
    process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT ?? "https://cloud.appwrite.io/v1",
  ).origin;
  const directives = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self'",
    `connect-src 'self' ${appwriteOrigin}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests",
  ];
  return directives.join("; ");
}

function applySecurityHeaders(response: NextResponse, nonce: string): void {
  response.headers.set("Content-Security-Policy", buildCsp(nonce));
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()",
  );
}

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");

  if (!isProtectedRoute(pathname)) {
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("x-nonce", nonce);
    const response = NextResponse.next({
      request: { headers: requestHeaders },
    });
    applySecurityHeaders(response, nonce);
    return response;
  }

  const token = request.cookies.get(SESSION_COOKIE)?.value;

  if (!token) {
    return NextResponse.redirect(new URL(LOGIN_URL, request.url));
  }

  try {
    const secret = new TextEncoder().encode(process.env.JWT_SECRET!);
    const { payload } = await jwtVerify(token, secret);
    const role = payload.role as string | undefined;
    const allowedPrefix = role ? JWT_ROLE_ROUTES[role] : undefined;

    if (!allowedPrefix || !pathname.startsWith(allowedPrefix)) {
      return NextResponse.redirect(new URL(LOGIN_URL, request.url));
    }

    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("x-nonce", nonce);
    requestHeaders.set("x-user-role", role);
    const response = NextResponse.next({ request: { headers: requestHeaders } });
    applySecurityHeaders(response, nonce);
    return response;
  } catch {
    // JWT is invalid or expired — clear the session cookie and force re-login
    const response = NextResponse.redirect(new URL(LOGIN_URL, request.url));
    response.cookies.set({
      name: SESSION_COOKIE,
      value: "",
      expires: new Date(0),
      path: "/",
    });
    return response;
  }
}

export const config = {
  matcher: [
    {
      source: "/((?!_next/static|_next/image|favicon.ico).*)",
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
