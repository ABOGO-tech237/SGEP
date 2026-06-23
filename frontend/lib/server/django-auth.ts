export class DjangoAuthError extends Error {
  constructor(
    message: string,
    public readonly code: "NOT_CONFIGURED" | "INVALID_CREDENTIALS" | "UNKNOWN",
  ) {
    super(message);
    this.name = "DjangoAuthError";
  }
}

export interface DjangoTokens {
  accessToken: string;
  refreshToken: string;
}

function getDjangoApiUrl(): string {
  const apiUrl = process.env.DJANGO_API_URL;
  if (!apiUrl) {
    throw new DjangoAuthError("DJANGO_API_URL missing", "NOT_CONFIGURED");
  }
  return apiUrl.endsWith("/") ? apiUrl : `${apiUrl}/`;
}

export async function loginWithDjango(
  email: string,
  password: string,
): Promise<DjangoTokens> {
  const response = await fetch(`${getDjangoApiUrl()}auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });

  if (response.status === 401) {
    throw new DjangoAuthError("Invalid credentials", "INVALID_CREDENTIALS");
  }

  if (!response.ok) {
    throw new DjangoAuthError("Django login failed", "UNKNOWN");
  }

  const payload = (await response.json()) as {
    access_token?: string;
    refresh_token?: string;
  };

  if (!payload.access_token || !payload.refresh_token) {
    throw new DjangoAuthError("Django tokens missing", "UNKNOWN");
  }

  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
  };
}

export async function refreshDjangoAccessToken(
  refreshToken: string,
): Promise<string | null> {
  const response = await fetch(`${getDjangoApiUrl()}auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
    cache: "no-store",
  });

  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as { access_token?: string };
  return payload.access_token ?? null;
}

export async function logoutDjango(
  refreshToken: string,
  accessToken?: string,
): Promise<void> {
  try {
    await fetch(`${getDjangoApiUrl()}auth/logout/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({ refresh: refreshToken }),
      cache: "no-store",
    });
  } catch {
    // Cookie is cleared even if Django logout fails.
  }
}
