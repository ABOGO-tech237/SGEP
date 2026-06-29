"use client";

const CSRF_COOKIE = "psms_csrf";

export function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(
    new RegExp(`(?:^|;)\\s*${CSRF_COOKIE}\\s*=\\s*([^;]+)`),
  );
  return match?.[1] ?? "";
}
