"use client";

import { LogOut } from "lucide-react";

import { useLogout } from "@/hooks/useLogout";

export function SignOutButton() {
  const logout = useLogout();

  return (
    <button
      type="button"
      onClick={() => void logout()}
      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
    >
      <LogOut className="size-4 shrink-0" />
      Sign out
    </button>
  );
}
