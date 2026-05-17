import { z } from "zod";
import type { UserRole } from "@/lib/auth/constants";

export const LoginSchema = z.object({
  email: z.email({ error: "Enter a valid email address." }),
  password: z.string().min(1, { error: "Password is required." }),
});

export type LoginFormValues = z.infer<typeof LoginSchema>;

export interface SessionUser {
  id: string;
  email: string;
  role: UserRole;
  name: string;
}

export interface LoginApiResponse {
  role: UserRole;
  user: SessionUser;
}
