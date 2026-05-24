import InactivityGuard from "@/components/InactivityGuard";

export default function ParentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <InactivityGuard>{children}</InactivityGuard>;
}
