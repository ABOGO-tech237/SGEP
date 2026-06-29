import InactivityGuard from "@/components/InactivityGuard";
import { AdminSidebar } from "@/components/admin/AdminSidebar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <InactivityGuard>
      <div className="flex h-screen bg-background text-foreground overflow-hidden">
        <AdminSidebar />
        <div className="flex-1 flex flex-col overflow-hidden">{children}</div>
      </div>
    </InactivityGuard>
  );
}
