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

export const TEAM_IDS: Record<UserRole, string> = {
  admin: process.env.NEXT_PUBLIC_APPWRITE_TEAM_ADMINS ?? "admins",
  teacher: process.env.NEXT_PUBLIC_APPWRITE_TEAM_TEACHERS ?? "teachers",
  student: process.env.NEXT_PUBLIC_APPWRITE_TEAM_STUDENTS ?? "students",
  parent: process.env.NEXT_PUBLIC_APPWRITE_TEAM_PARENTS ?? "parents",
};

/** Reverse map: Appwrite team ID → app role */
export const TEAM_ID_TO_ROLE: Record<string, UserRole> = Object.fromEntries(
  Object.entries(TEAM_IDS).map(([role, teamId]) => [teamId, role as UserRole]),
);
