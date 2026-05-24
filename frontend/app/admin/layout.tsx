import InactivityGuard from "@/components/InactivityGuard";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <InactivityGuard>{children}</InactivityGuard>;
}
