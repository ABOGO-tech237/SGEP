"use client";

import { useInactivity } from "@/hooks/useInactivity";
import { useLogout } from "@/hooks/useLogout";

const THIRTY_MINUTES_MS = 30 * 60 * 1000;

export default function InactivityGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  const logout = useLogout();
  useInactivity(THIRTY_MINUTES_MS, logout);
  return <>{children}</>;
}
