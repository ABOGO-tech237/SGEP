"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { LoginSchema, type LoginFormValues } from "@/lib/types/auth";
import { useAuth } from "@/context/AuthContext";
import { useSessionStore } from "@/stores/session";
import { ROLE_ROUTE_PREFIX } from "@/lib/auth/constants";

type StrengthLevel = "weak" | "fair" | "strong";

function getPasswordStrength(password: string): StrengthLevel | null {
  if (!password) return null;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const hasSymbol = /[^A-Za-z0-9]/.test(password);
  const types = [hasUpper, hasLower, hasDigit, hasSymbol].filter(
    Boolean,
  ).length;
  if (password.length < 8 || types < 2) return "weak";
  if (password.length >= 12 && types >= 3) return "strong";
  return "fair";
}

const STRENGTH_CONFIG: Record<
  StrengthLevel,
  { label: string; bars: number; color: string }
> = {
  weak: { label: "Weak", bars: 1, color: "bg-destructive" },
  fair: { label: "Fair", bars: 2, color: "bg-yellow-500" },
  strong: { label: "Strong", bars: 3, color: "bg-green-600" },
};

interface LoginFormProps {
  resetSuccess?: boolean;
}

export default function LoginForm({ resetSuccess }: LoginFormProps) {
  "use no memo";
  const router = useRouter();
  const queryClient = useQueryClient();
  const { login } = useAuth();
  const setUser = useSessionStore((s) => s.setUser);

  const [serverError, setServerError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(LoginSchema),
  });

  const password = watch("password", "");
  const strength = getPasswordStrength(password);

  async function onSubmit(data: LoginFormValues) {
    setServerError(null);
    try {
      const user = await login(data.email, data.password);
      const roleRes = await fetch("/api/auth/role", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: user.role }),
      });
      if (!roleRes.ok) {
        const body = await roleRes.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? "Session setup failed. Please try again.");
      }
      // Fetch Django token in the background — doesn't block navigation.
      // Backend may be sleeping (Render free tier); the token will be ready after wake-up.
      fetch("/api/auth/django", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: data.email, password: data.password }),
      }).catch(() => {});
      setUser(user);
      queryClient.clear();
      router.replace(ROLE_ROUTE_PREFIX[user.role]);
    } catch (err) {
      console.error("[login] failed:", err);
      const message =
        err instanceof Error ? err.message : "Something went wrong.";
      setServerError(message);
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      className="flex flex-col gap-5"
    >
      {resetSuccess && (
        <div
          role="status"
          className="rounded-md border border-green-600/30 bg-green-600/10 px-4 py-3 text-sm text-green-700"
        >
          Password updated — please sign in.
        </div>
      )}

      {serverError && (
        <div
          role="alert"
          aria-live="assertive"
          className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
        >
          {serverError}
        </div>
      )}

      <div className="flex flex-col gap-1.5">
        <label htmlFor="email" className="text-sm font-medium">
          Email address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          aria-describedby={errors.email ? "email-error" : undefined}
          aria-invalid={!!errors.email}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-offset-background transition focus-visible:ring-2 focus-visible:ring-ring aria-invalid:border-destructive"
          {...register("email")}
        />
        {errors.email && (
          <p id="email-error" className="text-xs text-destructive" role="alert">
            {errors.email.message}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between">
          <label htmlFor="password" className="text-sm font-medium">
            Password
          </label>
          <Link
            href="/forgot-password"
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Forgot password?
          </Link>
        </div>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            aria-describedby={
              errors.password
                ? "password-error"
                : strength
                  ? "password-strength"
                  : undefined
            }
            aria-invalid={!!errors.password}
            className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm outline-none ring-offset-background transition focus-visible:ring-2 focus-visible:ring-ring aria-invalid:border-destructive"
            {...register("password")}
          />
          <button
            type="button"
            aria-label={showPassword ? "Hide password" : "Show password"}
            onClick={() => setShowPassword((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            {showPassword ? (
              <EyeOff className="size-4" aria-hidden />
            ) : (
              <Eye className="size-4" aria-hidden />
            )}
          </button>
        </div>

        {strength && (
          <div id="password-strength" aria-live="polite">
            <div className="flex gap-1" aria-hidden>
              {[1, 2, 3].map((bar) => (
                <div
                  key={bar}
                  className={`h-1 flex-1 rounded-full transition-colors ${
                    bar <= STRENGTH_CONFIG[strength].bars
                      ? STRENGTH_CONFIG[strength].color
                      : "bg-muted"
                  }`}
                />
              ))}
            </div>
            <p className="sr-only">
              Password strength: {STRENGTH_CONFIG[strength].label}
            </p>
          </div>
        )}

        {errors.password && (
          <p
            id="password-error"
            className="text-xs text-destructive"
            role="alert"
          >
            {errors.password.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
