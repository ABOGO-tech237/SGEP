import { z } from "zod";
import type { SchoolUser } from "@/lib/auth";

export type LoginApiRole = "admin" | "teacher" | "student" | "parent";

export interface LoginApiResponse {
  role: LoginApiRole;
  user: SchoolUser;
}

export const LoginSchema = z.object({
  email: z.email({ error: "Enter a valid email address." }),
  password: z.string().min(1, { error: "Password is required." }),
});

export type LoginFormValues = z.infer<typeof LoginSchema>;

export const ForgotPasswordSchema = z.object({
  email: z.email({ error: "Enter a valid email address." }),
});

export type ForgotPasswordValues = z.infer<typeof ForgotPasswordSchema>;

export const ResetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, { error: "Password must be at least 8 characters." }),
    confirmPassword: z.string(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export type ResetPasswordValues = z.infer<typeof ResetPasswordSchema>;

export type { SchoolUser as SessionUser };
