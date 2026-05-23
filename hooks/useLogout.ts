"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useSessionStore } from "@/stores/session";
import { useAuth } from "@/context/AuthContext";

export function useLogout(): () => Promise<void> {
  const router = useRouter();
  const queryClient = useQueryClient();
  const clearUser = useSessionStore((s) => s.clearUser);
  const { logout } = useAuth();

  return useCallback(async () => {
    try {
      await logout();
    } finally {
      clearUser();
      queryClient.clear();
      router.replace("/login");
    }
  }, [router, queryClient, clearUser, logout]);
}
