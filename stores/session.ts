import { create } from "zustand";
import type { SessionUser } from "@/lib/types/auth";

interface SessionState {
  user: SessionUser | null;
  setUser: (user: SessionUser) => void;
  clearUser: () => void;
}

export const useSessionStore = create<SessionState>()((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),
}));
