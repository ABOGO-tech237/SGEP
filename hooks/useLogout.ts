"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useSessionStore } from "@/stores/session";
import { getCsrfToken } from "@/lib/client/csrf";

export function useLogout(): () => Promise<void> {
  const router = useRouter();
  const queryClient = useQueryClient();
  const clearUser = useSessionStore((s) => s.clearUser);

  return useCallback(async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: { "X-CSRF-Token": getCsrfToken() },
      });
    } finally {
      clearUser();
      queryClient.clear();
      router.replace("/login");
    }
  }, [router, queryClient, clearUser]);
}
