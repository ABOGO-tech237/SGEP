export const SESSION_COOKIE = "psms_session" as const;

export const USER_ROLES = {
  SUPER_ADMIN: "SUPER_ADMIN",
  ACCOUNTANT: "ACCOUNTANT",
  PARENT: "PARENT",
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

export const ROLE_ROUTE_PREFIX: Record<UserRole, string> = {
  SUPER_ADMIN: "/admin",
  ACCOUNTANT: "/accountant",
  PARENT: "/parent",
};
