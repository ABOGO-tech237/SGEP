import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import {
  ROLE_COOKIE,
  ROLE_ROUTE_PREFIX,
  type UserRole,
} from "@/lib/auth/constants";
import LoginForm from "./LoginForm";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Sign in — PSMS",
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ reset?: string }>;
}) {
  const cookieStore = await cookies();
  const role = cookieStore.get(ROLE_COOKIE)?.value as UserRole | undefined;
  if (role && ROLE_ROUTE_PREFIX[role]) {
    redirect(ROLE_ROUTE_PREFIX[role]);
  }

  const { reset } = await searchParams;

  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold tracking-tight">PSMS</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Primary School Management System
          </p>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold">
            Sign in to your account
          </h2>
          <LoginForm resetSuccess={reset === "success"} />
        </div>
      </div>
    </main>
  );
}
