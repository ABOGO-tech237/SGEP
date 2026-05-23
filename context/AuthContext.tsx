"use client";

import { createContext, useContext, useEffect, useState } from "react";
import {
  getAuthUser,
  login as appwriteLogin,
  logout as appwriteLogout,
  type SchoolUser,
} from "@/lib/auth";

interface AuthContextType {
  user: SchoolUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<SchoolUser>;
  logout: () => Promise<void>;
  isRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SchoolUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuthUser()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  async function handleLogin(email: string, password: string) {
    const loggedInUser = await appwriteLogin(email, password);
    setUser(loggedInUser);
    return loggedInUser;
  }

  async function handleLogout() {
    await appwriteLogout();
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
