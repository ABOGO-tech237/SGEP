import { redirect } from "next/navigation";
import ResetPasswordForm from "./ResetPasswordForm";

export const metadata = {
  title: "Set new password — PSMS",
};

export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ userId?: string; secret?: string }>;
}) {
  const { userId, secret } = await searchParams;

  if (!userId || !secret) {
    redirect("/forgot-password");
  }

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
          <h2 className="mb-5 text-lg font-semibold">Set a new password</h2>
          <ResetPasswordForm userId={userId} secret={secret} />
        </div>
      </div>
    </main>
  );
}
