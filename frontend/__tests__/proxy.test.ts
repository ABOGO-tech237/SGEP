// @vitest-environment node
import { describe, it, expect } from "vitest";
import { NextRequest } from "next/server";
import { SignJWT } from "jose";
import { proxy } from "../proxy";
import { SESSION_COOKIE } from "../lib/auth/constants";

const BASE_URL = "http://localhost:3000";
const SECRET = new TextEncoder().encode(process.env.JWT_SECRET!);

async function makeJwt(role: string): Promise<string> {
  return new SignJWT({ role, sub: "user-1" })
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime("1h")
    .sign(SECRET);
}

function request(path: string, cookie?: string): NextRequest {
  const req = new NextRequest(`${BASE_URL}${path}`);
  if (cookie) req.cookies.set(SESSION_COOKIE, cookie);
  return req;
}

describe("proxy — unauthenticated redirects", () => {
  it("redirects /admin to /login when no cookie", async () => {
    const res = await proxy(request("/admin/students"));
    expect(res.status).toBe(307);
    expect(res.headers.get("location")).toContain("/login");
  });

  it("redirects /accountant to /login when no cookie", async () => {
    const res = await proxy(request("/accountant/invoices"));
    expect(res.status).toBe(307);
    expect(res.headers.get("location")).toContain("/login");
  });

  it("redirects /parent to /login when no cookie", async () => {
    const res = await proxy(request("/parent/children"));
    expect(res.status).toBe(307);
    expect(res.headers.get("location")).toContain("/login");
  });
});

describe("proxy — public routes pass through", () => {
  it("allows /login without a session", async () => {
    const res = await proxy(request("/login"));
    expect(res.status).not.toBe(307);
  });

  it("allows /api/health without a session", async () => {
    const res = await proxy(request("/api/health"));
    expect(res.status).not.toBe(307);
  });
});

describe("proxy — RBAC enforcement", () => {
  it("lets SUPER_ADMIN access /admin", async () => {
    const token = await makeJwt("SUPER_ADMIN");
    const res = await proxy(request("/admin/students", token));
    expect(res.status).not.toBe(307);
  });

  it("blocks SUPER_ADMIN from /accountant", async () => {
    const token = await makeJwt("SUPER_ADMIN");
    const res = await proxy(request("/accountant/invoices", token));
    expect(res.status).toBe(307);
    expect(res.headers.get("location")).toContain("/login");
  });

  it("lets ACCOUNTANT access /accountant", async () => {
    const token = await makeJwt("ACCOUNTANT");
    const res = await proxy(request("/accountant/invoices", token));
    expect(res.status).not.toBe(307);
  });

  it("blocks ACCOUNTANT from /admin", async () => {
    const token = await makeJwt("ACCOUNTANT");
    const res = await proxy(request("/admin/students", token));
    expect(res.status).toBe(307);
  });

  it("lets PARENT access /parent", async () => {
    const token = await makeJwt("PARENT");
    const res = await proxy(request("/parent/children", token));
    expect(res.status).not.toBe(307);
  });
});

describe("proxy — security headers", () => {
  it("sets X-Frame-Options: DENY on all responses", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("X-Frame-Options")).toBe("DENY");
  });

  it("sets X-Content-Type-Options: nosniff on all responses", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("X-Content-Type-Options")).toBe("nosniff");
  });

  it("sets CSP with frame-ancestors none", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("Content-Security-Policy")).toContain(
      "frame-ancestors 'none'",
    );
  });

  it("sets CSP with nonce on script-src", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("Content-Security-Policy")).toMatch(/nonce-[A-Za-z0-9+/=]+/);
  });

  it("sets Referrer-Policy", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("Referrer-Policy")).toBe(
      "strict-origin-when-cross-origin",
    );
  });

  it("sets Permissions-Policy", async () => {
    const res = await proxy(request("/login"));
    expect(res.headers.get("Permissions-Policy")).toBe(
      "camera=(), microphone=(), geolocation=()",
    );
  });
});

describe("proxy — invalid token", () => {
  it("redirects and clears cookie when JWT is tampered", async () => {
    const res = await proxy(request("/admin/students", "invalid.jwt.token"));
    expect(res.status).toBe(307);
    const setCookie = res.headers.get("set-cookie");
    expect(setCookie).toContain(SESSION_COOKIE);
    // Cookie cleared when session is expired: Expires set to epoch or Max-Age=0
    expect(setCookie).toMatch(/Expires=Thu, 01 Jan 1970|Max-Age=0/);
  });
});
