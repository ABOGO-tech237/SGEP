import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  ROLE_ROUTE_PREFIX,
  ROLE_COOKIE,
  type UserRole,
} from "@/lib/auth/constants";

const LOGIN_URL = "/login";

function getAppwriteSessionCookie(): string {
  const projectId = process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID;
  if (!projectId) throw new Error("NEXT_PUBLIC_APPWRITE_PROJECT_ID is not set");
  return `a_session_${projectId}`;
}

function buildCsp(nonce: string): string {
  const isDev = process.env.NODE_ENV === "development";
  const directives = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self'",
    "connect-src 'self'",
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

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");

  const isProtectedRoute =
    pathname.startsWith("/admin") ||
    pathname.startsWith("/teacher") ||
    pathname.startsWith("/student") ||
    pathname.startsWith("/parent");

  if (!isProtectedRoute) {
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("x-nonce", nonce);
    const response = NextResponse.next({
      request: { headers: requestHeaders },
    });
    applySecurityHeaders(response, nonce);
    return response;
  }

  const sessionCookie = request.cookies.get(getAppwriteSessionCookie())?.value;
  if (!sessionCookie) {
    return NextResponse.redirect(new URL(LOGIN_URL, request.url));
  }

  const role = request.cookies.get(ROLE_COOKIE)?.value as UserRole | undefined;
  const allowedPrefix = role ? ROLE_ROUTE_PREFIX[role] : undefined;

  if (!allowedPrefix || !pathname.startsWith(allowedPrefix)) {
    return NextResponse.redirect(new URL(LOGIN_URL, request.url));
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("x-user-role", role!);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  applySecurityHeaders(response, nonce);
  return response;
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
