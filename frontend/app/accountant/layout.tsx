import InactivityGuard from "@/components/InactivityGuard";

export default function AccountantLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <InactivityGuard>{children}</InactivityGuard>;
}
