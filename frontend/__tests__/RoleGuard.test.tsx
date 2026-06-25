import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { RoleGuard } from "@/components/ui/RoleGuard";
import { useSessionStore } from "@/stores/session";
import type { SessionUser } from "@/lib/types/auth";

function setStoreUser(user: SessionUser | null) {
  useSessionStore.setState({ user });
}

const adminUser: SessionUser = {
  id: "1",
  email: "admin@school.cm",
  role: "admin",
  name: "Admin",
  teamId: "admins",
};

const parentUser: SessionUser = {
  id: "2",
  email: "parent@school.cm",
  role: "parent",
  name: "Parent",
  teamId: "parents",
};

beforeEach(() => {
  useSessionStore.setState({ user: null });
});

describe("RoleGuard", () => {
  it("renders children when user role is in allowedRoles", () => {
    setStoreUser(adminUser);
    render(
      <RoleGuard allowedRoles={["admin"]}>
        <span>Admin content</span>
      </RoleGuard>
    );
    expect(screen.getByText("Admin content")).toBeInTheDocument();
  });

  it("hides children when user role is not in allowedRoles", () => {
    setStoreUser(parentUser);
    render(
      <RoleGuard allowedRoles={["admin"]}>
        <span>Admin content</span>
      </RoleGuard>
    );
    expect(screen.queryByText("Admin content")).not.toBeInTheDocument();
  });

  it("hides children when user is null", () => {
    setStoreUser(null);
    render(
      <RoleGuard allowedRoles={["admin"]}>
        <span>Protected</span>
      </RoleGuard>
    );
    expect(screen.queryByText("Protected")).not.toBeInTheDocument();
  });

  it("renders fallback when role is not allowed", () => {
    setStoreUser(parentUser);
    render(
      <RoleGuard allowedRoles={["admin"]} fallback={<span>No access</span>}>
        <span>Admin only</span>
      </RoleGuard>
    );
    expect(screen.getByText("No access")).toBeInTheDocument();
    expect(screen.queryByText("Admin only")).not.toBeInTheDocument();
  });

  it("supports multiple allowed roles", () => {
    setStoreUser(parentUser);
    render(
      <RoleGuard allowedRoles={["admin", "parent"]}>
        <span>Shared content</span>
      </RoleGuard>
    );
    expect(screen.getByText("Shared content")).toBeInTheDocument();
  });
});
