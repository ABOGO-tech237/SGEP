"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { SchoolUser } from "@/lib/auth";

interface AuthContextType {
  user: SchoolUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<SchoolUser>;
  logout: () => Promise<void>;
  isRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

async function fetchSessionUser(): Promise<SchoolUser | null> {
  const response = await fetch("/api/auth/me", { cache: "no-store" });
  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as { user?: SchoolUser };
  return payload.user ?? null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SchoolUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessionUser()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  async function handleLogin(email: string, password: string) {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const payload = (await response.json().catch(() => null)) as
      | { user?: SchoolUser; error?: string }
      | null;

    if (!response.ok || !payload?.user) {
      throw new Error(payload?.error ?? "Login failed.");
    }

    setUser(payload.user);
    return payload.user;
  }

  async function handleLogout() {
    const csrfToken = document.cookie
      .split("; ")
      .find((entry) => entry.startsWith("psms_csrf="))
      ?.split("=")[1];

    if (csrfToken) {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: { "X-CSRF-Token": csrfToken },
      });
    }

    await fetch("/api/auth/role", { method: "DELETE" });
    setUser(null);
  }

  function isRole(...roles: string[]) {
    if (!user) return false;
    return roles.includes(user.role);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: handleLogin,
        logout: handleLogout,
        isRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
