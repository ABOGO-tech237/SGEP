export const USER_ROLES = {
  ADMIN: "admin",
  TEACHER: "teacher",
  STUDENT: "student",
  PARENT: "parent",
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

export const ROLE_ROUTE_PREFIX: Record<UserRole, string> = {
  admin: "/admin",
  teacher: "/teacher",
  student: "/student",
  parent: "/parent",
};

export const SESSION_COOKIE =
  `a_session_${process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID}` as const;
export const ROLE_COOKIE = "user_role" as const;
