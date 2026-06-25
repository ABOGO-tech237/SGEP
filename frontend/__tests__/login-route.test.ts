// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SignJWT } from "jose";

const cookieStore = new Map<string, string>();

const { loginWithDjango } = vi.hoisted(() => ({
  loginWithDjango: vi.fn(),
}));

vi.mock("next/headers", () => ({
  cookies: vi.fn(async () => ({
    set: (name: string, value: string) => {
      cookieStore.set(name, value);
    },
    get: (name: string) => {
      const value = cookieStore.get(name);
      return value ? { name, value } : undefined;
    },
    delete: (name: string) => {
      cookieStore.delete(name);
    },
  })),
}));

vi.mock("@/lib/server/django-auth", () => ({
  DjangoAuthError: class DjangoAuthError extends Error {
    constructor(
      message: string,
      public readonly code: string,
    ) {
      super(message);
      this.name = "DjangoAuthError";
    }
  },
  loginWithDjango,
}));

import { POST } from "../app/api/auth/login/route";
import {
  DJANGO_ACCESS_COOKIE,
  DJANGO_REFRESH_COOKIE,
} from "../lib/auth/constants";

async function makeAccessToken(claims: Record<string, unknown>): Promise<string> {
  return new SignJWT(claims)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("30m")
    .sign(new TextEncoder().encode("test-secret"));
}

describe("POST /api/auth/login", () => {
  beforeEach(() => {
    loginWithDjango.mockReset();
    cookieStore.clear();
  });

  it("returns 400 for invalid payload", async () => {
    const response = await POST(
      new Request("http://localhost:3000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "bad", password: "" }),
      }),
    );

    expect(response.status).toBe(400);
    expect(loginWithDjango).not.toHaveBeenCalled();
  });

  it("authenticates via Django and returns user payload with normalized role", async () => {
    const accessToken = await makeAccessToken({
      role: "superadmin",
      email: "admin@sgep.cm",
      user_id: "user-1",
    });
    loginWithDjango.mockResolvedValue({
      accessToken,
      refreshToken: "django-refresh",
    });

    const response = await POST(
      new Request("http://localhost:3000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "admin@sgep.cm",
          password: "AdminPassword123!",
        }),
      }),
    );

    expect(response.status).toBe(200);
    expect(loginWithDjango).toHaveBeenCalledWith(
      "admin@sgep.cm",
      "AdminPassword123!",
    );

    const body = (await response.json()) as {
      role: string;
      user: { email: string; id: string };
    };
    expect(body.role).toBe("admin");
    expect(body.user.email).toBe("admin@sgep.cm");
    expect(body.user.id).toBe("user-1");
    expect(cookieStore.get(DJANGO_ACCESS_COOKIE)).toBe(accessToken);
    expect(cookieStore.get(DJANGO_REFRESH_COOKIE)).toBe("django-refresh");
  });

  it("returns 401 for invalid credentials", async () => {
    const { DjangoAuthError } = await import("@/lib/server/django-auth");
    loginWithDjango.mockRejectedValue(
      new DjangoAuthError("invalid", "INVALID_CREDENTIALS"),
    );

    const response = await POST(
      new Request("http://localhost:3000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "admin@sgep.cm",
          password: "wrong",
        }),
      }),
    );

    expect(response.status).toBe(401);
  });

  it("returns 503 when Django is not configured", async () => {
    const { DjangoAuthError } = await import("@/lib/server/django-auth");
    loginWithDjango.mockRejectedValue(
      new DjangoAuthError("missing", "NOT_CONFIGURED"),
    );

    const response = await POST(
      new Request("http://localhost:3000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "admin@sgep.cm",
          password: "secret",
        }),
      }),
    );

    expect(response.status).toBe(503);
  });
});
